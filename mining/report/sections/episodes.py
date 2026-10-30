from __future__ import annotations
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Spacer
from ...analysis import Analysis
from ...charts import LINE
from ...detection import TESTS, Episode
from ..components import (
    banner,
    chart_image,
    format_number,
    key_value_table,
    paragraph,
    section_title,
    side_by_side,
)
from ..context import ReportContext
from ..theme import CONTENT_WIDTH, EPISODE_COLORS, EPISODE_TEXT_COLORS

FACTS_WIDTH = 72 * mm
FACT_KEY_WIDTH = 30 * mm
FACT_VALUE_WIDTH = 40 * mm
CHART_SIZE = (6.4, 3.6)
CHART_ASPECT = 0.6
INTRODUCTION = (
    "Each episode groups consecutive flagged days of one series. The expected value is the "
    "median of nearby non-anomalous days, adjusted for trend and weekday pattern when that "
    "option is enabled."
)
NO_EPISODES = "No anomalies were detected with the selected tests and parameters."

def episode_sections(context: ReportContext) -> list:
    story = [PageBreak(), section_title(6, "Anomaly details")]
    if not context.analysis.episodes:
        return [*story, paragraph(NO_EPISODES)]
    story += [paragraph(INTRODUCTION), Spacer(1, 4 * mm)]
    return story + [_episode_block(context, episode) for episode in context.analysis.episodes]

def _episode_block(context: ReportContext, episode: Episode) -> KeepTogether:
    title = f"{episode.id} &nbsp;·&nbsp; {episode.kind.upper()} &nbsp;·&nbsp; {episode.series}"
    chart_width = CONTENT_WIDTH - FACTS_WIDTH
    body = side_by_side(
        key_value_table(_facts(context.analysis, episode), FACT_KEY_WIDTH, FACT_VALUE_WIDTH),
        chart_image(_chart(context, episode), chart_width, CHART_ASPECT),
        FACTS_WIDTH,
        chart_width,
    )
    return KeepTogether(
        [
            banner(title, EPISODE_COLORS[episode.kind], EPISODE_TEXT_COLORS[episode.kind]),
            Spacer(1, 2 * mm),
            body,
            Spacer(1, 7 * mm),
        ]
    )

def _facts(analysis: Analysis, episode: Episode) -> list[list[str]]:
    test_results = analysis.results[episode.series].loc[episode.dates]
    facts = [
        ["Period", episode.period_label()],
        ["Peak day", f"{episode.peak_date:%A, %d %b %Y}"],
        ["Peak value", f"{format_number(episode.peak_value)} t"],
        ["Expected", f"{format_number(episode.expected)} t"],
        ["Deviation", f"{episode.deviation_pct:+.1f}%"],
        ["Max |z-score|", format_number(episode.max_abs_z, 2)],
    ]
    return facts + [[test, "Flagged" if test_results[test].any() else "-"] for test in TESTS]

def _chart(context: ReportContext, episode: Episode) -> bytes:
    window, flags = context.analysis.episode_context(episode)
    return context.chart_png(
        [episode.series],
        LINE,
        flags,
        output=window,
        with_trend=False,
        highlight=(episode.start, episode.end),
        expected=episode.expected,
        size=CHART_SIZE,
    )
