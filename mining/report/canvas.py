from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .theme import (
    ACCENT,
    BRAND_DARK,
    COMPANY,
    COVER_BAND_WIDTH,
    FOOTER_NOTE,
    MARGIN,
    MUTED_TEXT,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    REPORT_TITLE,
    RULE,
)

HEADER_RULE_Y = PAGE_HEIGHT - 12 * mm
HEADER_TEXT_Y = PAGE_HEIGHT - 10 * mm
FOOTER_RULE_Y = 12 * mm
FOOTER_TEXT_Y = 8 * mm
HEADER_ACCENT_WIDTH = 24 * mm
COVER_PAGE_NUMBER = 1


class DecoratedPageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._page_states = []

    def showPage(self):
        self._page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._page_states)
        for state in self._page_states:
            self.__dict__.update(state)
            if self._pageNumber == COVER_PAGE_NUMBER:
                self._draw_cover_band()
            else:
                self._draw_header()
                self._draw_footer(page_count)
            super().showPage()
        super().save()

    def _draw_cover_band(self) -> None:
        self.saveState()
        self.setFillColor(ACCENT)
        self.rect(0, 0, COVER_BAND_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
        self.setFillColor(BRAND_DARK)
        self.rect(COVER_BAND_WIDTH, 0, COVER_BAND_WIDTH / 4, PAGE_HEIGHT, stroke=0, fill=1)
        self.restoreState()

    def _draw_rule(self, y: float) -> None:
        self.setStrokeColor(RULE)
        self.setLineWidth(0.6)
        self.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)

    def _draw_header(self) -> None:
        self.saveState()
        self._draw_rule(HEADER_RULE_Y)
        self.setStrokeColor(ACCENT)
        self.setLineWidth(1.6)
        self.line(MARGIN, HEADER_RULE_Y, MARGIN + HEADER_ACCENT_WIDTH, HEADER_RULE_Y)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(BRAND_DARK)
        self.drawString(MARGIN, HEADER_TEXT_Y, COMPANY.upper())
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        self.drawRightString(PAGE_WIDTH - MARGIN, HEADER_TEXT_Y, REPORT_TITLE)
        self.restoreState()

    def _draw_footer(self, page_count: int) -> None:
        self.saveState()
        self._draw_rule(FOOTER_RULE_Y)
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        self.drawString(MARGIN, FOOTER_TEXT_Y, FOOTER_NOTE)
        page_label = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN, FOOTER_TEXT_Y, page_label)
        self.restoreState()
