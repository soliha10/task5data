from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import CondPageBreak, KeepTogether, PageBreak, Spacer, Table

from ... import stats
from ...data import series_label
from ...detection import Episode
from ..components import (
    chart_image,
    data_table,
    equal_widths,
    format_number,
    paragraph,
    section_title,
)
from ..context import ReportContext
from ..theme import CONTENT_WIDTH

STAT_COLUMNS = [stats.MEAN, stats.STD, stats.MEDIAN, stats.IQR, stats.MIN, stats.MAX]
EPISODE_HEADER = ["ID", "Type", "Period", "Peak value", "Expected", "Deviation", "Detected by"]
EPISODE_FIXED_WIDTHS = [12 * mm, 16 * mm, 46 * mm, 20 * mm, 20 * mm, 20 * mm]
EPISODE_NUMERIC_COLUMNS = (3, 5)
CHART_SIZE = (10, 3.4)
CHART_ASPECT = 0.37
MIN_SPACE_FOR_SECTION = 120 * mm


def mine_sections(context: ReportContext) -> list:
    story = [PageBreak(), section_title(5, "Mine details")]
    for name in context.analysis.output.columns:
        story += _mine_section(context, name)
    return story


def _mine_section(context: ReportContext, name: str) -> list:
    chart = context.chart_png(
        [name], context.single_series_kind, context.analysis.flags_of(name), size=CHART_SIZE
    )
    heading = [
        paragraph(series_label(name), "h2"),
        _statistics_table(context, name),
        Spacer(1, 3 * mm),
        chart_image(chart, aspect=CHART_ASPECT),
    ]
    return [
        CondPageBreak(MIN_SPACE_FOR_SECTION),
        KeepTogether(heading),
        *_episodes_block(context.analysis.episodes_of(name)),
        Spacer(1, 6 * mm),
    ]


def _statistics_table(context: ReportContext, name: str) -> Table:
    summary = context.analysis.summary
    header = [*STAT_COLUMNS, "Total"]
    values = [format_number(summary.at[name, column]) for column in STAT_COLUMNS]
    values.append(format_number(summary.at[name, stats.TOTAL_OUTPUT], 0))
    return data_table([header, values], equal_widths(len(header)), numeric_columns=(0, -1))


def _episodes_block(episodes: list[Episode]) -> list:
    if not episodes:
        return [paragraph("No anomalies detected with the selected tests.", "note")]
    rows = [EPISODE_HEADER] + [_episode_row(episode) for episode in episodes]
    widths = [*EPISODE_FIXED_WIDTHS, CONTENT_WIDTH - sum(EPISODE_FIXED_WIDTHS)]
    return [Spacer(1, 2 * mm), data_table(rows, widths, numeric_columns=EPISODE_NUMERIC_COLUMNS)]


def _episode_row(episode: Episode) -> list:
    return [
        episode.id,
        episode.kind,
        episode.period_label(),
        format_number(episode.peak_value),
        format_number(episode.expected),
        f"{episode.deviation_pct:+.1f}%",
        paragraph(", ".join(episode.tests), "cell"),
    ]
