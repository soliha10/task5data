from __future__ import annotations

import pandas as pd
import streamlit as st

from mining import charts
from mining.analysis import Analysis
from mining.detection import Episode, episodes_table

NO_ANOMALIES_MESSAGE = "No anomalies detected with the selected tests and parameters."
INFO_METRIC = dict(delta_color="off", delta_arrow="off", border=True)


def styled(frame: pd.DataFrame, digits: int = 1):
    return frame.style.format(precision=digits, thousands=",")


def show_chart(
    analysis: Analysis,
    series: list[str],
    kind: str,
    trend_degree: int | None,
    *,
    title: str | None = None,
    flagged: charts.FlagMap | None = None,
    output: pd.DataFrame | None = None,
    highlight: charts.Span | None = None,
    height: int = 440,
    key: str | None = None,
) -> None:
    figure = charts.build_figure(
        analysis.output if output is None else output,
        series,
        kind,
        trend_degree,
        analysis.flagged if flagged is None else flagged,
        charts.series_colors(analysis.output.columns),
        title=title,
        highlight=highlight,
        height=height,
    )
    st.plotly_chart(figure, width="stretch", key=key)


def show_episodes_table(episodes: list[Episode]) -> None:
    st.dataframe(
        styled(episodes_table(episodes)),
        hide_index=True,
        width="stretch",
        column_config={"Deviation %": st.column_config.NumberColumn(format="%+.1f%%")},
    )
