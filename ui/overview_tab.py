from __future__ import annotations

import streamlit as st

from mining import charts
from mining.analysis import Analysis
from mining.data import TOTAL

from .components import show_chart, styled
from .controls import Controls

STACKED_CAPTION = (
    "Stacked view shows the selected mines stacked into the daily total; "
    "outlined segments are anomalies."
)


def render_overview_tab(analysis: Analysis, controls: Controls) -> None:
    series = st.multiselect("Series", list(analysis.output.columns), default=analysis.mines)
    if controls.chart_kind == charts.STACKED:
        st.caption(STACKED_CAPTION)
    show_chart(
        analysis,
        series or analysis.mines,
        controls.chart_kind,
        controls.trend_degree,
        title="Daily output by mine",
    )

    st.subheader("Descriptive statistics")
    st.dataframe(styled(analysis.summary), width="stretch")
    st.caption("Tons. Std dev is the sample standard deviation; IQR = Q3 − Q1.")

    st.subheader("Flagged days by test")
    st.dataframe(analysis.flag_counts, width="stretch")
    st.caption("“Any selected” counts days flagged by at least one highlighted test.")

    show_chart(
        analysis,
        [TOTAL],
        controls.single_series_kind,
        controls.trend_degree,
        title="Total daily output",
        flagged=analysis.flags_of(TOTAL),
        height=360,
    )
