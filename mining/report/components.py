from __future__ import annotations
import io
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from .theme import (
    BODY_TEXT,
    BRAND_DARK,
    CONTENT_WIDTH,
    EMPHASIS,
    PAPER,
    RULE,
    SERIES_COLUMN_WIDTH,
    STYLES,
    ZEBRA,
)

ALL_CELLS = ((0, 0), (-1, -1))
HEADER_ROW = ((0, 0), (-1, 0))
BODY_ROWS = ((0, 1), (-1, -1))
LAST_ROW = ((0, -1), (-1, -1))
DATA_TABLE_STYLE = [
    ("BACKGROUND", *HEADER_ROW, BRAND_DARK),
    ("TEXTCOLOR", *HEADER_ROW, PAPER),
    ("FONTNAME", *HEADER_ROW, "Helvetica-Bold"),
    ("FONTNAME", *BODY_ROWS, "Helvetica"),
    ("FONTSIZE", *ALL_CELLS, 8),
    ("TEXTCOLOR", *BODY_ROWS, BODY_TEXT),
    ("VALIGN", *ALL_CELLS, "MIDDLE"),
    ("ROWBACKGROUNDS", *BODY_ROWS, [PAPER, ZEBRA]),
    ("LINEBELOW", *ALL_CELLS, 0.4, RULE),
    ("TOPPADDING", *ALL_CELLS, 4),
    ("BOTTOMPADDING", *ALL_CELLS, 4),
]
KEY_VALUE_STYLE = [
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", *ALL_CELLS, 8.5),
    ("TEXTCOLOR", (0, 0), (0, -1), BRAND_DARK),
    ("TEXTCOLOR", (1, 0), (1, -1), BODY_TEXT),
    ("LINEBELOW", *ALL_CELLS, 0.4, RULE),
    ("VALIGN", *ALL_CELLS, "TOP"),
    ("TOPPADDING", *ALL_CELLS, 4),
    ("BOTTOMPADDING", *ALL_CELLS, 4),
]
KPI_STRIP_STYLE = [
    ("BOX", *ALL_CELLS, 0.6, RULE),
    ("INNERGRID", *ALL_CELLS, 0.6, RULE),
    ("BACKGROUND", *ALL_CELLS, EMPHASIS),
    ("TOPPADDING", *ALL_CELLS, 8),
    ("BOTTOMPADDING", *ALL_CELLS, 8),
    ("LEFTPADDING", *ALL_CELLS, 8),
]

def format_number(value: float, digits: int = 1) -> str:
    return f"{float(value):,.{digits}f}"

def paragraph(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])

def section_title(number: int, title: str) -> Paragraph:
    return paragraph(f"{number}. {title}", "h1")

def series_table_widths(value_columns: int) -> list[float]:
    value_width = (CONTENT_WIDTH - SERIES_COLUMN_WIDTH) / value_columns
    return [SERIES_COLUMN_WIDTH] + [value_width] * value_columns

def equal_widths(columns: int) -> list[float]:
    return [CONTENT_WIDTH / columns] * columns

def data_table(
    rows: list[list],
    col_widths: list[float],
    numeric_columns: tuple[int, int] = (1, -1),
    emphasize_last_row: bool = False,
) -> Table:
    first, last = numeric_columns
    style = [*DATA_TABLE_STYLE, ("ALIGN", (first, 0), (last, -1), "RIGHT")]
    if emphasize_last_row:
        style += [("FONTNAME", *LAST_ROW, "Helvetica-Bold"), ("BACKGROUND", *LAST_ROW, EMPHASIS)]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style))
    return table

def key_value_table(rows: list[list], key_width: float, value_width: float) -> Table:
    table = Table(rows, colWidths=[key_width, value_width])
    table.setStyle(TableStyle(KEY_VALUE_STYLE))
    return table

def chart_image(png: bytes, width: float = CONTENT_WIDTH, aspect: float = 0.46) -> Image:
    return Image(io.BytesIO(png), width=width, height=width * aspect)

def kpi_strip(items: list[tuple[str, str]]) -> Table:
    cell_width = CONTENT_WIDTH / len(items)
    cells = [_kpi_cell(label, value, cell_width - 6) for label, value in items]
    table = Table([cells], colWidths=[cell_width] * len(items))
    table.setStyle(TableStyle(KPI_STRIP_STYLE))
    return table

def banner(text: str, background, text_color) -> Table:
    style = ParagraphStyle("banner_text", parent=STYLES["banner"], textColor=text_color)
    table = Table([[Paragraph(text, style)]], colWidths=[CONTENT_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", *ALL_CELLS, background),
                ("LEFTPADDING", *ALL_CELLS, 8),
                ("TOPPADDING", *ALL_CELLS, 5),
                ("BOTTOMPADDING", *ALL_CELLS, 5),
            ]
        )
    )
    return table

def side_by_side(left, right, left_width: float, right_width: float) -> Table:
    table = Table([[left, right]], colWidths=[left_width, right_width])
    table.setStyle(TableStyle([("VALIGN", *ALL_CELLS, "TOP"), ("LEFTPADDING", *ALL_CELLS, 0)]))
    return table

def _kpi_cell(label: str, value: str, width: float) -> Table:
    return Table(
        [[paragraph(value, "kpi_value")], [paragraph(label.upper(), "kpi_label")]],
        colWidths=[width],
    )
