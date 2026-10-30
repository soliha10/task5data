import pandas as pd
from mining.analysis import analyze
from mining.data import TOTAL
from mining.detection import DROP, GRUBBS, IQR, SPIKE, TESTS, ZSCORE, DetectionParams

POINT_TESTS = (IQR, ZSCORE, GRUBBS)

def _output(series: pd.Series) -> pd.DataFrame:
    output = pd.DataFrame({"LV-426": series})
    output[TOTAL] = output.sum(axis=1)
    return output

def test_spike_becomes_single_episode(series_with_spike):
    analysis = analyze(_output(series_with_spike), DetectionParams(adjust=False), TESTS)
    episodes = analysis.episodes_of("LV-426")
    assert len(episodes) == 1
    assert episodes[0].kind == SPIKE
    assert episodes[0].peak_date == series_with_spike.index[20]
    assert episodes[0].deviation_pct > 100

def test_consecutive_days_are_grouped_into_one_drop(steady_series):
    series = steady_series.copy()
    series.iloc[10:13] = 5.0
    analysis = analyze(_output(series), DetectionParams(adjust=False), POINT_TESTS)
    episode = analysis.episodes_of("LV-426")[0]
    assert episode.kind == DROP
    assert episode.days == 3
    assert episode.period_label().endswith("(3 days)")

def test_no_selected_tests_means_no_episodes(series_with_spike):
    analysis = analyze(_output(series_with_spike), DetectionParams(), tests=())
    assert analysis.episodes == []
    assert analysis.flag_counts["Any selected"].sum() == 0

def test_episode_ids_follow_chronological_order(series_with_spike):
    series = series_with_spike.copy()
    series.iloc[5] = 1.0
    analysis = analyze(_output(series), DetectionParams(adjust=False), TESTS)
    starts = [episode.start for episode in analysis.episodes]
    assert starts == sorted(starts)
    assert [episode.id for episode in analysis.episodes][:2] == ["A01", "A02"]
