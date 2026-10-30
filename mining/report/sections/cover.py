from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Spacer, Table

from ... import stats
from ..components import format_number, key_value_table, kpi_strip, paragraph
from ..context import ReportContext
from ..theme import COMPANY, CONTENT_WIDTH, MUTED_TEXT_ON_TINT_HEX, REPORT_TITLE

DETAILS_KEY_WIDTH = 48 * mm


def cover_page(context: ReportContext) -> list:
    return [
        Spacer(1, 30 * mm),
        paragraph(COMPANY.upper(), "brand"),
        Spacer(1, 4 * mm),
        paragraph(REPORT_TITLE.replace("&", "&amp;"), "title"),
        Spacer(1, 3 * mm),
        paragraph(_subtitle(context), "subtitle"),
        Spacer(1, 14 * mm),
        _kpis(context),
        Spacer(1, 12 * mm),
        _details(context),
        PageBreak(),
    ]


def _subtitle(context: ReportContext) -> str:
    index = context.analysis.output.index
    period = f"{index[0]:%d %b %Y} - {index[-1]:%d %b %Y}"
    return f"Daily resource extraction · {len(context.analysis.mines)} mines · {period}"


def _kpis(context: ReportContext) -> Table:
    analysis = context.analysis
    anomalies = (
        f"{len(analysis.episodes)} <font size=10 color='{MUTED_TEXT_ON_TINT_HEX}'>"
        f"({analysis.spike_count} / {analysis.drop_count})</font>"
    )
    return kpi_strip(
        [
            ("Total output (t)", format_number(analysis.total_stat(stats.TOTAL_OUTPUT), 0)),
            ("Mean daily total (t)", format_number(analysis.total_stat(stats.MEAN))),
            ("Days analysed", str(len(analysis.output))),
            ("Anomalies (spikes / drops)", anomalies),
        ]
    )


def _details(context: ReportContext) -> Table:
    settings, analysis = context.settings, context.analysis
    trend = f"polynomial degree {settings.trend_degree}" if settings.trend_degree else "none"
    rows = [
        ["Report generated", f"{settings.generated_at:%d %b %Y, %H:%M}"],
        ["Mines", ", ".join(analysis.mines)],
        ["Data source", paragraph(settings.source_url, "cell")],
        ["Chart type / trendline", f"{settings.chart_kind} / {trend}"],
        ["Tests used for highlighting", ", ".join(analysis.tests) or "none"],
    ]
    return key_value_table(rows, DETAILS_KEY_WIDTH, CONTENT_WIDTH - DETAILS_KEY_WIDTH)
