import numpy as np
import pandas as pd
import pytest

DAYS = 42
BASE_OUTPUT = 50.0
WAVE_AMPLITUDE = 2.0
WAVE_FREQUENCY = 0.7

@pytest.fixture
def dates() -> pd.DatetimeIndex:
    return pd.date_range("2099-11-02", periods=DAYS, freq="D")

@pytest.fixture
def steady_series(dates) -> pd.Series:
    wave = WAVE_AMPLITUDE * np.sin(np.arange(len(dates)) * WAVE_FREQUENCY)
    return pd.Series(BASE_OUTPUT + wave, index=dates)

@pytest.fixture
def series_with_spike(steady_series) -> pd.Series:
    series = steady_series.copy()
    series.iloc[20] = BASE_OUTPUT * 3
    return series
