from __future__ import annotations
import streamlit as st
from mining import stats
from mining.analysis import Analysis
from mining.data import series_label
from mining.detection import TESTS
from .components import INFO_METRIC, NO_ANOMALIES_MESSAGE, show_chart, show_episodes_table, styled
from .controls import Controls

DETAIL_COLUMNS = ["value", "adjusted", "z", "ma_dev_pct", *TESTS]

def render_mine_tab(analysis: Analysis, controls: Controls) -> None:
    name = st.selectbox("Mine", list(analysis.output.columns), format_func=series_label)
    _render_mine_metrics(analysis, name)
    show_chart(
        analysis,
        [name],
        controls.single_series_kind,
        controls.trend_degree,
        title=series_label(name),
        flagged=analysis.flags_of(name),
    )
    _render_mine_episodes(analysis, name)
    with st.expander("Per-day test results"):
        st.dataframe(styled(analysis.results[name][DETAIL_COLUMNS], 2), width="stretch")

def _render_mine_metrics(analysis: Analysis, name: str) -> None:
    row = analysis.summary.loc[name]
    quartiles = f"Q1 {row[stats.Q1]:,.1f} · Q3 {row[stats.Q3]:,.1f}"
    mean, std, median, iqr = st.columns(4)
    mean.metric("Mean daily output", f"{row[stats.MEAN]:,.1f} t", border=True)
    std.metric("Standard deviation", f"{row[stats.STD]:,.1f} t", border=True)
    median.metric("Median", f"{row[stats.MEDIAN]:,.1f} t", border=True)
    iqr.metric("Interquartile range", f"{row[stats.IQR]:,.1f} t", quartiles, **INFO_METRIC)

def _render_mine_episodes(analysis: Analysis, name: str) -> None:
    episodes = analysis.episodes_of(name)
    st.subheader(f"Anomalies · {len(episodes)}")
    if episodes:
        show_episodes_table(episodes)
    else:
        st.info(NO_ANOMALIES_MESSAGE)
