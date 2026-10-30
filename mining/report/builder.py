from __future__ import annotations

import io

from reportlab.platypus import SimpleDocTemplate

from ..analysis import Analysis
from .canvas import DecoratedPageCanvas
from .context import ReportContext, ReportSettings
from .sections import SECTION_BUILDERS
from .theme import COMPANY, MARGIN, PAGE_SIZE, REPORT_TITLE


def build_report(analysis: Analysis, settings: ReportSettings) -> bytes:
    context = ReportContext.create(analysis, settings)
    story = [flowable for build_section in SECTION_BUILDERS for flowable in build_section(context)]

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=REPORT_TITLE,
        author=COMPANY,
    )
    document.build(story, canvasmaker=DecoratedPageCanvas)
    return buffer.getvalue()
