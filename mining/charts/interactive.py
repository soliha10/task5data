from __future__ import annotations
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
    flags_for,
    has_flags,
    polynomial_trend,
    stack_members,
    trend_label,
)

SYMBOLS = {SPIKE: "triangle-up", DROP: "triangle-down"}
TRANSPARENT = "rgba(0,0,0,0)"
HOVER_POINT = "%{x|%b %d, %Y}<br>%{y:.1f} t"
STACK_OUTLINE_WIDTH = 3
STACK_GROUP = "stack"

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
    _apply_layout(figure, title, height)
    return figure

def _hover_template(name: str) -> str:
    return f"<b>{name}</b><br>{HOVER_POINT}<extra></extra>"

def _flag_hover_template(name: str, direction: str) -> str:
    return f"<b>{name} · {direction}</b><br>{HOVER_POINT}<br>%{{customdata}}<extra></extra>"

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
    bases = output[members].cumsum(axis=1) - output[members]
    for name in members:
        figure.add_bar(
            x=output.index,
            y=output[name],
            base=bases[name],
            name=name,
            offsetgroup=STACK_GROUP,
            marker_color=colors[name],
            hovertemplate=_hover_template(name),
        )
    for name in members:
        _add_flag_bars(figure, name, flags_for(flagged, name), STACK_GROUP, bases[name])
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
            offsetgroup=name,
            marker_color=color,
            hovertemplate=_hover_template(name),
        )
        _add_flag_bars(figure, name, flags, name)
    if trend_degree:
        _add_trend(figure, output.index, output[name], trend_degree, f"{name} trend", color, 1.6)

def _add_flag_markers(figure: go.Figure, name: str, flags: pd.DataFrame) -> None:
    for direction, rows in flags.groupby("direction"):
        figure.add_scatter(
            x=rows.index,
            y=rows["value"],
            mode="markers",
            name=direction,
            legendgroup=direction,
            showlegend=False,
            marker=dict(
                size=12,
                line=dict(color=DIRECTION_OUTLINES[direction], width=1.5),
                color=DIRECTION_COLORS[direction],
                symbol=SYMBOLS[direction],
            ),
            customdata=rows["tests"],
            hovertemplate=_flag_hover_template(name, direction),
        )

def _add_flag_bars(
    figure: go.Figure,
    name: str,
    flags: pd.DataFrame,
    offsetgroup: str,
    bases: pd.Series | None = None,
) -> None:
    for direction, rows in flags.groupby("direction"):
        color = DIRECTION_COLORS[direction]
        outlined = bases is not None
        figure.add_bar(
            x=rows.index,
            y=rows["value"],
            base=bases.loc[rows.index] if outlined else None,
            name=direction,
            legendgroup=direction,
            showlegend=False,
            offsetgroup=offsetgroup,
            marker=dict(
                color=TRANSPARENT if outlined else color,
                line=dict(color=color, width=STACK_OUTLINE_WIDTH if outlined else 0),
            ),
            customdata=rows["tests"],
            hovertemplate=_flag_hover_template(name, direction),
        )

def _add_direction_legend(figure: go.Figure) -> None:
    for direction, color in DIRECTION_COLORS.items():
        figure.add_scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=direction,
            legendgroup=direction,
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

def _apply_layout(figure: go.Figure, title: str | None, height: int) -> None:
    figure.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16, color=TITLE_COLOR))
        if title
        else None,
        template="plotly_white",
        height=height,
        barmode="group",
        bargap=0.15,
        margin=dict(l=10, r=10, t=50 if title else 30, b=70),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
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
