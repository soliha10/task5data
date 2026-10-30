import pandas as pd
import pytest
from mining.detection.outlier_tests import (
    grubbs_outliers,
    iqr_outliers,
    neighbour_moving_average,
    remove_trend_and_weekday,
    z_scores,
)

SPIKE_POSITION = 20

def test_iqr_rule_flags_only_the_spike(series_with_spike):
    flags = iqr_outliers(series_with_spike, k=1.5)
    assert flags.iloc[SPIKE_POSITION]
    assert flags.sum() == 1

def test_z_scores_are_standardised(steady_series):
    scores = z_scores(steady_series)
    assert scores.mean() == pytest.approx(0, abs=1e-9)
    assert scores.std(ddof=1) == pytest.approx(1)

def test_z_scores_of_constant_series_are_zero(dates):
    assert (z_scores(pd.Series(5.0, index=dates)) == 0).all()

def test_moving_average_excludes_the_day_itself(series_with_spike):
    average, deviation_pct = neighbour_moving_average(series_with_spike, window=7)
    neighbours = series_with_spike.iloc[SPIKE_POSITION - 3 : SPIKE_POSITION + 4].drop(
        series_with_spike.index[SPIKE_POSITION]
    )
    assert average.iloc[SPIKE_POSITION] == pytest.approx(neighbours.mean())
    assert deviation_pct.iloc[SPIKE_POSITION] > 100

def test_grubbs_detects_spike_and_ignores_clean_data(series_with_spike, steady_series):
    assert grubbs_outliers(series_with_spike, alpha=0.05).iloc[SPIKE_POSITION]
    assert not grubbs_outliers(steady_series, alpha=0.05).any()

def test_adjustment_removes_weekday_pattern(steady_series):
    is_weekday = steady_series.index.day_of_week < 5
    weekend_dip = steady_series.where(is_weekday, steady_series * 0.6)
    adjusted = remove_trend_and_weekday(weekend_dip)
    assert adjusted[~is_weekday].mean() == pytest.approx(adjusted[is_weekday].mean(), rel=0.05)
