from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ..detection import DROP, SPIKE
from .theme import (
    DATE_TICK_FORMAT,
    DIRECTION_COLORS,
    DIRECTION_OUTLINES,
    FONT_STACK,
    GRID_COLOR,
    HIGHLIGHT_COLOR,
    HOVER_BACKGROUND,
    HOVER_BORDER,
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

SYMBOLS = {SPIKE: "triangle-up", DROP: "triangle-down"}
TRANSPARENT = "rgba(0,0,0,0)"
HOVER_POINT = "%{x|%b %d, %Y}<br>%{y:.1f} t"
STACK_OUTLINE_WIDTH = 3


def build_figure(
    output: pd.DataFrame,
    series: list[str],
    kind: str,
    trend_degree: int | None,
    flagged: FlagMap,
    colors: ColorMap,
    title: str | None = None,
    highlight: Span | None = None,
    height: int = 440,
) -> go.Figure:
    figure = go.Figure()
    if kind == STACKED:
        _add_stack(figure, output, series, trend_degree, flagged, colors)
    else:
        for name in series:
            flags = flags_for(flagged, name)
            _add_series(figure, output, name, kind, trend_degree, flags, colors[name])
    if has_flags(flagged):
        _add_direction_legend(figure)
    if highlight:
        _add_highlight(figure, highlight)
    _apply_layout(figure, title, height, barmode="stack" if kind == STACKED else "group")
    return figure


def _hover_template(name: str) -> str:
    return f"<b>{name}</b><br>{HOVER_POINT}<extra></extra>"


def _add_trend(
    figure: go.Figure, x, values: pd.Series, degree: int, name: str, color: str, width: float
) -> None:
    figure.add_scatter(
        x=x,
        y=polynomial_trend(values, degree),
        mode="lines",
        name=name,
        line=dict(color=color, width=width, dash="dash"),
        hoverinfo="skip",
    )


def _add_stack(
    figure: go.Figure,
    output: pd.DataFrame,
    series: list[str],
    trend_degree: int | None,
    flagged: FlagMap,
    colors: ColorMap,
) -> None:
    members = stack_members(output, series)
    for name in members:
        flags = flags_for(flagged, name)
        figure.add_bar(
            x=output.index,
            y=output[name],
            name=name,
            marker_color=colors[name],
            marker_line_color=colors_by_date(output.index, flags, TRANSPARENT),
            marker_line_width=widths_by_date(output.index, flags, STACK_OUTLINE_WIDTH),
            hovertemplate=_hover_template(name),
        )
    if trend_degree:
        _add_trend(
            figure,
            output.index,
            output[members].sum(axis=1),
            trend_degree,
            trend_label(trend_degree),
            TOTAL_COLOR,
            2.5,
        )


def _add_series(
    figure: go.Figure,
    output: pd.DataFrame,
    name: str,
    kind: str,
    trend_degree: int | None,
    flags: pd.DataFrame,
    color: str,
) -> None:
    if kind == LINE:
        figure.add_scatter(
            x=output.index,
            y=output[name],
            mode="lines",
            name=name,
            line=dict(color=color, width=2),
            hovertemplate=_hover_template(name),
        )
        if not flags.empty:
            _add_flag_markers(figure, name, flags)
    else:
        figure.add_bar(
            x=output.index,
            y=output[name],
            name=name,
            marker_color=colors_by_date(output.index, flags, color),
            hovertemplate=_hover_template(name),
        )
    if trend_degree:
        _add_trend(figure, output.index, output[name], trend_degree, f"{name} trend", color, 1.6)


def _add_flag_markers(figure: go.Figure, name: str, flags: pd.DataFrame) -> None:
    directions = flags["direction"]
    figure.add_scatter(
        x=flags.index,
        y=flags["value"],
        mode="markers",
        showlegend=False,
        marker=dict(
            size=12,
            line=dict(color=[DIRECTION_OUTLINES[d] for d in directions], width=1.5),
            color=[DIRECTION_COLORS[d] for d in directions],
            symbol=[SYMBOLS[d] for d in directions],
        ),
        customdata=np.stack([directions, flags["tests"]], axis=-1),
        hovertemplate=(
            f"<b>{name} · %{{customdata[0]}}</b><br>{HOVER_POINT}"
            "<br>%{customdata[1]}<extra></extra>"
        ),
    )


def _add_direction_legend(figure: go.Figure) -> None:
    for direction, color in DIRECTION_COLORS.items():
        figure.add_scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=direction,
            marker=dict(
                color=color,
                size=11,
                symbol=SYMBOLS[direction],
                line=dict(color=DIRECTION_OUTLINES[direction], width=1.5),
            ),
        )


def _add_highlight(figure: go.Figure, highlight: Span) -> None:
    half_day = pd.Timedelta(hours=12)
    figure.add_vrect(
        x0=highlight[0] - half_day,
        x1=highlight[1] + half_day,
        fillcolor=HIGHLIGHT_COLOR,
        opacity=0.8,
        line_width=0,
        layer="below",
    )


def _apply_layout(figure: go.Figure, title: str | None, height: int, barmode: str) -> None:
    figure.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color=TITLE_COLOR)) if title else None,
        template="plotly_white",
        height=height,
        barmode=barmode,
        bargap=0.15,
        margin=dict(l=10, r=10, t=60 if title else 30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=HOVER_BACKGROUND,
            bordercolor=HOVER_BORDER,
            font=dict(family=FONT_STACK, color=TITLE_COLOR),
        ),
        font=dict(family=FONT_STACK, color=TEXT_COLOR),
    )
    figure.update_yaxes(
        title_text=Y_AXIS_TITLE, gridcolor=GRID_COLOR, zeroline=False, rangemode="tozero"
    )
    figure.update_xaxes(gridcolor=GRID_COLOR, tickformat=DATE_TICK_FORMAT)
