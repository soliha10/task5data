from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats as sps

MIN_DAYS_FOR_ADJUSTMENT = 14
MIN_GRUBBS_SAMPLE = 3
GRUBBS_MAX_OUTLIER_SHARE = 0.25

def remove_trend_and_weekday(series: pd.Series) -> pd.Series:
    values = series.astype(float)
    if len(values) < MIN_DAYS_FOR_ADJUSTMENT:
        return values
    trend = _linear_trend(values)
    weekday_factors = _weekday_factors(values, trend)
    adjusted = values.to_numpy() / (trend * weekday_factors) * np.nanmean(trend)
    return pd.Series(adjusted, index=values.index).fillna(values)

def iqr_outliers(values: pd.Series, k: float) -> pd.Series:
    first_quartile, third_quartile = values.quantile(0.25), values.quantile(0.75)
    margin = k * (third_quartile - first_quartile)
    return (values < first_quartile - margin) | (values > third_quartile + margin)

def z_scores(values: pd.Series) -> pd.Series:
    std = values.std(ddof=1)
    if not std or np.isnan(std):
        return pd.Series(0.0, index=values.index)
    return (values - values.mean()) / std

def neighbour_moving_average(values: pd.Series, window: int) -> tuple[pd.Series, pd.Series]:
    rolling = values.rolling(window, center=True, min_periods=2)
    average = (rolling.sum() - values) / (rolling.count() - 1)
    deviation_pct = (values - average) / average.abs() * 100
    return average, deviation_pct

def grubbs_outliers(values: pd.Series, alpha: float) -> pd.Series:
    remaining = values.dropna().astype(float)
    max_outliers = max(1, int(len(remaining) * GRUBBS_MAX_OUTLIER_SHARE))
    outlier_dates = []
    while len(remaining) >= MIN_GRUBBS_SAMPLE and len(outlier_dates) < max_outliers:
        candidate = _grubbs_candidate(remaining, alpha)
        if candidate is None:
            break
        outlier_dates.append(candidate)
        remaining = remaining.drop(candidate)
    return pd.Series(values.index.isin(outlier_dates), index=values.index)

def _linear_trend(values: pd.Series) -> np.ndarray:
    day_index = np.arange(len(values), dtype=float)
    trend = np.polynomial.Polynomial.fit(day_index, values.to_numpy(), 1)(day_index)
    return np.where(trend > 1e-9, trend, np.nan)

def _weekday_factors(values: pd.Series, trend: np.ndarray) -> np.ndarray:
    weekdays = values.index.day_of_week
    ratio = pd.Series(values.to_numpy() / trend, index=values.index)
    factors = ratio.groupby(weekdays).median()
    factors = factors / factors.mean()
    return weekdays.map(factors).to_numpy(dtype=float)

def _grubbs_candidate(values: pd.Series, alpha: float):
    mean, std = values.mean(), values.std(ddof=1)
    if not std:
        return None
    candidate = (values - mean).abs().idxmax()
    statistic = abs(values[candidate] - mean) / std
    return candidate if statistic > _grubbs_critical_value(len(values), alpha) else None

def _grubbs_critical_value(sample_size: int, alpha: float) -> float:
    t = sps.t.ppf(1 - alpha / (2 * sample_size), sample_size - 2)
    return (sample_size - 1) / np.sqrt(sample_size) * np.sqrt(t * t / (sample_size - 2 + t * t))
