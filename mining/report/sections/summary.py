from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Spacer

from ... import stats
from ...analysis import Analysis
from ...data import TOTAL
from ...detection import DetectionParams
from ..components import data_table, format_number, paragraph, section_title, series_table_widths
from ..context import ReportContext

STAT_COLUMNS = [
    stats.MEAN,
    stats.STD,
    stats.MEDIAN,
    stats.Q1,
    stats.Q3,
    stats.IQR,
    stats.MIN,
    stats.MAX,
]
DAYS_PER_WEEK = 7


def executive_summary(context: ReportContext) -> list:
    findings = _findings(context.analysis)
    return [section_title(1, "Executive summary")] + [
        paragraph(f"&bull;&nbsp;&nbsp;{finding}") for finding in findings
    ]


def statistics_section(context: ReportContext) -> list:
    summary = context.analysis.summary
    header = ["Series", *STAT_COLUMNS, "Total"]
    rows = [header] + [
        [
            name,
            *(format_number(summary.at[name, column]) for column in STAT_COLUMNS),
            format_number(summary.at[name, stats.TOTAL_OUTPUT], 0),
        ]
        for name in summary.index
    ]
    return [
        Spacer(1, 6 * mm),
        section_title(2, "Descriptive statistics"),
        data_table(rows, series_table_widths(len(header) - 1), emphasize_last_row=True),
        paragraph(
            "All values in tons. Std dev is the sample standard deviation; IQR = Q3 - Q1.", "note"
        ),
    ]


def flag_counts_section(context: ReportContext) -> list:
    counts = context.analysis.flag_counts
    rows = [["Series", *counts.columns]] + [
        [name, *(str(counts.at[name, column]) for column in counts.columns)]
        for name in counts.index
    ]
    return [
        Spacer(1, 6 * mm),
        section_title(3, "Anomalies by test"),
        data_table(rows, series_table_widths(len(counts.columns)), emphasize_last_row=True),
        paragraph(_parameters_note(context.analysis.params), "note"),
    ]


def _findings(analysis: Analysis) -> list[str]:
    findings = [
        _output_finding(analysis),
        _mine_ranking_finding(analysis),
        _weekly_change_finding(analysis),
        f"<b>{len(analysis.episodes)}</b> anomaly episodes were detected "
        f"({analysis.spike_count} spikes, {analysis.drop_count} drops).",
    ]
    if analysis.episodes:
        findings.append(_largest_deviation_finding(analysis))
    return findings


def _output_finding(analysis: Analysis) -> str:
    total = format_number(analysis.total_stat(stats.TOTAL_OUTPUT), 0)
    mean = format_number(analysis.total_stat(stats.MEAN))
    median = format_number(analysis.total_stat(stats.MEDIAN))
    iqr = format_number(analysis.total_stat(stats.IQR))
    return (
        f"Total output over the period was <b>{total} t</b>, an average of "
        f"<b>{mean} t/day</b> (median {median}, IQR {iqr})."
    )


def _mine_ranking_finding(analysis: Analysis) -> str:
    summary, mines = analysis.summary, analysis.mines
    top = analysis.top_mine
    most_volatile = (summary.loc[mines, stats.STD] / summary.loc[mines, stats.MEAN]).idxmax()
    top_mean = format_number(summary.at[top, stats.MEAN])
    return (
        f"<b>{top}</b> is the most productive mine ({top_mean} t/day); "
        f"<b>{most_volatile}</b> is the most volatile relative to its mean."
    )


def _weekly_change_finding(analysis: Analysis) -> str:
    total = analysis.output[TOTAL]
    first_week = total.iloc[:DAYS_PER_WEEK].mean()
    last_week = total.iloc[-DAYS_PER_WEEK:].mean()
    change = (last_week - first_week) / first_week * 100 if first_week else 0.0
    return f"Average daily total in the last week is <b>{change:+.1f}%</b> versus the first week."


def _largest_deviation_finding(analysis: Analysis) -> str:
    largest = max(analysis.episodes, key=lambda episode: abs(episode.deviation_pct))
    return (
        f"The largest deviation was a <b>{largest.kind.lower()}</b> at "
        f"<b>{largest.series}</b> on {largest.peak_date:%d %b %Y} "
        f"({largest.deviation_pct:+.1f}% vs expected)."
    )


def _parameters_note(params: DetectionParams) -> str:
    adjustment = "on" if params.adjust else "off"
    return (
        f"Number of flagged days. Parameters: IQR k = {params.iqr_k}; "
        f"|z| &gt; {params.z_threshold}; moving average window {params.ma_window} days, "
        f"threshold {params.ma_pct:g}%; Grubbs alpha = {params.grubbs_alpha}; "
        f"trend &amp; weekday adjustment {adjustment}."
    )
