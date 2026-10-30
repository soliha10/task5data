from __future__ import annotations
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Spacer
from ...data import TOTAL
from ..components import chart_image, section_title
from ..context import ReportContext

def overview_section(context: ReportContext) -> list:
    analysis = context.analysis
    mines_chart = context.chart_png(
        analysis.mines, context.settings.chart_kind, analysis.flagged, title="Daily output by mine"
    )
    total_chart = context.chart_png(
        [TOTAL], context.single_series_kind, analysis.flags_of(TOTAL), title="Total daily output"
    )
    return [
        PageBreak(),
        section_title(4, "Output overview"),
        chart_image(mines_chart),
        Spacer(1, 4 * mm),
        chart_image(total_chart),
    ]
