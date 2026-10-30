from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Spacer

from ...detection import DetectionParams
from ..components import paragraph, section_title
from ..context import ReportContext

ADJUSTMENT_ON = (
    "Each series is divided by a fitted linear trend and by a median weekday factor before "
    "testing, so regular weekend dips and growth are not reported as anomalies."
)
ADJUSTMENT_OFF = "Disabled: tests are applied to raw values."


def methodology_section(context: ReportContext) -> list:
    story = [PageBreak(), section_title(7, "Methodology")]
    for title, text in _items(context.analysis.params):
        story += [paragraph(f"<b>{title}.</b> {text}"), Spacer(1, 2 * mm)]
    return story


def _items(params: DetectionParams) -> list[tuple[str, str]]:
    return [
        (
            "Data",
            "Daily output per mine is read from the generator Google Spreadsheet "
            "(Data sheet). Total is the sum of all mines.",
        ),
        ("Adjustment", ADJUSTMENT_ON if params.adjust else ADJUSTMENT_OFF),
        (
            "IQR rule",
            f"A day is an outlier if it lies below Q1 - k&middot;IQR or above "
            f"Q3 + k&middot;IQR (k = {params.iqr_k}).",
        ),
        ("Z-score", f"z = (x - mean) / std; a day is an outlier if |z| &gt; {params.z_threshold}."),
        (
            "Moving average",
            f"Centred {params.ma_window}-day moving average of neighbouring "
            f"days (excluding the day itself); outlier if the day deviates by "
            f"more than {params.ma_pct:g}%.",
        ),
        (
            "Grubbs' test",
            f"Iterative two-sided Grubbs test at significance alpha = "
            f"{params.grubbs_alpha}; the most extreme value is removed while G "
            f"exceeds the critical value.",
        ),
        (
            "Trendline",
            "Least-squares polynomial of the selected degree fitted against the day index.",
        ),
        (
            "Episodes",
            "Flagged days of the same series at most one day apart form a single "
            "spike or drop episode.",
        ),
    ]
