from __future__ import annotations

import io

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from ..detection import DROP, SPIKE
from .theme import (
    AXIS_COLOR,
    DATE_TICK_FORMAT,
    DIRECTION_COLORS,
    DIRECTION_OUTLINES,
    EXPECTED_COLOR,
    GRID_COLOR,
    HIGHLIGHT_COLOR,
    LINE,
    STACKED,
    TEXT_COLOR,
    TITLE_COLOR,
    TOTAL_COLOR,
    Y_AXIS_TITLE,
    ColorMap,
    FlagMap,
    Span,
    colors_by_date,
    flags_for,
    has_flags,
    polynomial_trend,
    stack_members,
    trend_label,
    widths_by_date,
)

MARKERS = {SPIKE: "^", DROP: "v"}
PNG_DPI = 200
BAR_WIDTH = 0.8
STACK_OUTLINE_WIDTH = 2.2
DEFAULT_SIZE = (10, 4.2)


def render_png(
    output: pd.DataFrame,
    series: list[str],
    kind: str,
    trend_degree: int | None,
    flagged: FlagMap,
    colors: ColorMap,
    title: str | None = None,
    highlight: Span | None = None,
    expected: float | None = None,
    size: tuple[float, float] = DEFAULT_SIZE,
) -> bytes:
    figure = Figure(figsize=size, dpi=PNG_DPI)
    axes = figure.subplots()
    x = mdates.date2num(output.index.to_pydatetime())

    if kind == STACKED:
        _draw_stack(axes, x, output, series, trend_degree, flagged, colors)
    else:
        _draw_series(axes, x, output, series, kind, trend_degree, flagged, colors)
    _draw_annotations(axes, highlight, expected)
    _style_axes(axes, x, title)
    _add_legend(axes, show_directions=has_flags(flagged))
    return _to_png(figure)


def _draw_stack(
    axes: Axes,
    x,
    output: pd.DataFrame,
    series: list[str],
    trend_degree: int | None,
    flagged: FlagMap,
    colors: ColorMap,
) -> None:
    members = stack_members(output, series)
    bottom = np.zeros(len(output))
    for name in members:
        flags = flags_for(flagged, name)
        axes.bar(
            x,
            output[name],
            BAR_WIDTH,
            bottom=bottom,
            color=colors[name],
            label=name,
            edgecolor=colors_by_date(output.index, flags, "none"),
            linewidth=widths_by_date(output.index, flags, STACK_OUTLINE_WIDTH),
        )
        bottom += output[name].to_numpy()
    if trend_degree:
        total = output[members].sum(axis=1)
        axes.plot(
            x,
            polynomial_trend(total, trend_degree),
            color=TOTAL_COLOR,
            lw=2,
            ls="--",
            label=trend_label(trend_degree),
        )


def _draw_series(
    axes: Axes,
    x,
    output: pd.DataFrame,
    series: list[str],
    kind: str,
    trend_degree: int | None,
    flagged: FlagMap,
    colors: ColorMap,
) -> None:
    bar_width = BAR_WIDTH / max(len(series), 1)
    for position, name in enumerate(series):
        flags = flags_for(flagged, name)
        if kind == LINE:
            axes.plot(x, output[name], color=colors[name], lw=1.8, label=name)
            _draw_flag_markers(axes, flags)
        else:
            offset = (position - (len(series) - 1) / 2) * bar_width
            axes.bar(
                x + offset,
                output[name],
                bar_width,
                label=name,
                color=colors_by_date(output.index, flags, colors[name]),
            )
        if trend_degree:
            axes.plot(
                x, polynomial_trend(output[name], trend_degree), color=colors[name], lw=1.3, ls="--"
            )


def _draw_flag_markers(axes: Axes, flags: pd.DataFrame) -> None:
    for direction, marker in MARKERS.items():
        points = flags[flags["direction"] == direction]
        if not points.empty:
            axes.scatter(
                mdates.date2num(points.index.to_pydatetime()),
                points["value"],
                marker=marker,
                s=60,
                color=DIRECTION_COLORS[direction],
                edgecolor=DIRECTION_OUTLINES[direction],
                linewidth=0.8,
                zorder=5,
            )


def _draw_annotations(axes: Axes, highlight: Span | None, expected: float | None) -> None:
    if highlight:
        start, end = mdates.date2num(highlight[0]), mdates.date2num(highlight[1])
        axes.axvspan(start - 0.5, end + 0.5, color=HIGHLIGHT_COLOR, alpha=0.9, zorder=0)
    if expected is not None:
        axes.axhline(expected, color=EXPECTED_COLOR, lw=1, ls=":", label="Expected at peak")


def _style_axes(axes: Axes, x, title: str | None) -> None:
    axes.spines[["top", "right"]].set_visible(False)
    axes.spines[["left", "bottom"]].set_color(AXIS_COLOR)
    axes.tick_params(colors=TEXT_COLOR, labelsize=8)
    axes.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.set_ylabel(Y_AXIS_TITLE, color=TEXT_COLOR, fontsize=9)
    axes.xaxis.set_major_formatter(mdates.DateFormatter(DATE_TICK_FORMAT))
    axes.set_xlim(x[0] - 0.7, x[-1] + 0.7)
    axes.set_ylim(bottom=0)
    if title:
        axes.set_title(title, loc="left", fontsize=11, color=TITLE_COLOR, fontweight="bold", pad=10)


def _direction_handles() -> list[Line2D]:
    return [
        Line2D(
            [],
            [],
            marker=MARKERS[direction],
            ls="none",
            color=color,
            markeredgecolor=DIRECTION_OUTLINES[direction],
            label=direction,
            markersize=7,
        )
        for direction, color in DIRECTION_COLORS.items()
    ]


def _add_legend(axes: Axes, show_directions: bool) -> None:
    handles, _ = axes.get_legend_handles_labels()
    if show_directions:
        handles += _direction_handles()
    axes.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0, -0.12),
        ncol=min(6, len(handles)),
        frameon=False,
        fontsize=8,
    )


def _to_png(figure: Figure) -> bytes:
    figure.tight_layout()
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight")
    return buffer.getvalue()
