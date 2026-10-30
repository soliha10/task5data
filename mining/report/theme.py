from __future__ import annotations
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from .. import brand
from ..detection import DROP, SPIKE

PAPER = HexColor(brand.WHITE)
INK = HexColor(brand.TEXT)
BODY_TEXT = HexColor(brand.TEXT_BODY)
MUTED_TEXT = HexColor(brand.TEXT_MUTED)
MUTED_TEXT_ON_TINT = HexColor(brand.TEXT_MUTED_ON_TINT)
RULE = HexColor(brand.BORDER)
ZEBRA = HexColor(brand.SURFACE)
EMPHASIS = HexColor(brand.SUBTLE_BACKGROUND)
ACCENT = HexColor(brand.ACTION)
BRAND_DARK = HexColor(brand.BRAND_DARK)
SUBHEADING = HexColor(brand.PRIMARY_800)
EPISODE_COLORS = {SPIKE: HexColor(brand.SPIKE), DROP: HexColor(brand.DROP)}
EPISODE_TEXT_COLORS = {SPIKE: PAPER, DROP: INK}
MUTED_TEXT_ON_TINT_HEX = brand.TEXT_MUTED_ON_TINT
PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
SERIES_COLUMN_WIDTH = 30 * mm
COVER_BAND_WIDTH = 7 * mm
COMPANY = "Weyland-Yutani Corporation"
REPORT_TITLE = "Mining Output & Anomaly Report"
FOOTER_NOTE = "Confidential - internal use only"

def _build_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    def style(name: str, parent: str = "BodyText", **options) -> ParagraphStyle:
        return ParagraphStyle(name, parent=sample[parent], **options)
    bold = "Helvetica-Bold"
    return {
        "brand": style("brand", fontName=bold, fontSize=10, leading=14, textColor=ACCENT),
        "title": style(
            "title",
            "Title",
            fontName=bold,
            fontSize=26,
            leading=31,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "subtitle": style("subtitle", "Normal", fontSize=13, leading=18, textColor=MUTED_TEXT),
        "h1": style(
            "h1",
            "Heading1",
            fontName=bold,
            fontSize=16,
            leading=20,
            textColor=BRAND_DARK,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "h2": style(
            "h2",
            "Heading2",
            fontName=bold,
            fontSize=12.5,
            leading=16,
            textColor=SUBHEADING,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": style("body", fontSize=9.5, leading=14, textColor=BODY_TEXT),
        "note": style("note", fontSize=8, leading=11, textColor=MUTED_TEXT),
        "cell": style("cell", fontSize=8, leading=10, textColor=BODY_TEXT),
        "banner": style("banner", fontName=bold, fontSize=10.5, leading=14, textColor=PAPER),
        "kpi_value": style(
            "kpi_value", fontName=bold, fontSize=16, leading=20, textColor=BRAND_DARK
        ),
        "kpi_label": style(
            "kpi_label",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=MUTED_TEXT_ON_TINT,
        ),
    }

STYLES = _build_styles()
