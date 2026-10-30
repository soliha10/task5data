from __future__ import annotations

import numpy as np
import pandas as pd

from .. import brand
from ..data import TOTAL
from ..detection import DROP, SPIKE

LINE, BAR, STACKED = "Line", "Bar", "Stacked"
KINDS = (LINE, BAR, STACKED)

PALETTE = brand.CATEGORICAL
TOTAL_COLOR = brand.BRAND_DARK
SPIKE_COLOR = brand.SPIKE
DROP_COLOR = brand.DROP
GRID_COLOR = brand.BORDER
TEXT_COLOR = brand.TEXT_BODY
TITLE_COLOR = brand.TEXT
AXIS_COLOR = brand.AXIS
HIGHLIGHT_COLOR = brand.SUBTLE_ACCENT
EXPECTED_COLOR = brand.TEXT_MUTED
MARKER_OUTLINE_COLOR = brand.WHITE
HOVER_BACKGROUND = brand.WHITE
HOVER_BORDER = brand.ACTION
FONT_STACK = brand.FONT_STACK
DIRECTION_COLORS = {SPIKE: SPIKE_COLOR, DROP: DROP_COLOR}
DIRECTION_OUTLINES = {SPIKE: MARKER_OUTLINE_COLOR, DROP: brand.DROP_OUTLINE}

Y_AXIS_TITLE = "Output (tons)"
DATE_TICK_FORMAT = "%b %d"

FlagMap = dict[str, pd.DataFrame]
ColorMap = dict[str, str]
Span = tuple[pd.Timestamp, pd.Timestamp]

_EMPTY_FLAG_COLUMNS = ["value", "direction", "tests"]


def series_colors(columns) -> ColorMap:
    mines = [name for name in columns if name != TOTAL]
    colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(mines)}
    colors[TOTAL] = TOTAL_COLOR
    return colors


def single_series_kind(kind: str) -> str:
    return BAR if kind == STACKED else kind


def polynomial_trend(values: pd.Series, degree: int) -> np.ndarray:
    day_index = np.arange(len(values), dtype=float)
    degree = max(1, min(degree, len(values) - 1))
    fitted = np.polynomial.Polynomial.fit(day_index, values.to_numpy(dtype=float), degree)
    return fitted(day_index)


def trend_label(degree: int) -> str:
    return f"Trend (deg {degree})"


def flags_for(flagged: FlagMap, name: str) -> pd.DataFrame:
    return flagged.get(name, pd.DataFrame(columns=_EMPTY_FLAG_COLUMNS))


def has_flags(flagged: FlagMap) -> bool:
    return any(not flags.empty for flags in flagged.values())


def stack_members(output: pd.DataFrame, series: list[str]) -> list[str]:
    members = [name for name in series if name != TOTAL]
    return members or [name for name in output.columns if name != TOTAL]


def colors_by_date(dates, flags: pd.DataFrame, default: str) -> list[str]:
    return [
        DIRECTION_COLORS[flags.at[date, "direction"]] if date in flags.index else default
        for date in dates
    ]


def widths_by_date(dates, flags: pd.DataFrame, width: float) -> list[float]:
    return [width if date in flags.index else 0 for date in dates]
