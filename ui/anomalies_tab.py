from __future__ import annotations

import streamlit as st

from mining import charts
from mining.analysis import Analysis
from mining.detection import Episode

from .components import NO_ANOMALIES_MESSAGE, show_chart, show_episodes_table

EPISODES_CAPTION = (
    "Consecutive flagged days of the same series (at most one day apart) form one episode. "
    "Expected = median of nearby normal days, mapped onto the peak day."
)
EPISODE_CHART_HEIGHT = 280


def render_anomalies_tab(analysis: Analysis) -> None:
    if not analysis.episodes:
        st.info(NO_ANOMALIES_MESSAGE)
        return
    show_episodes_table(analysis.episodes)
    st.caption(EPISODES_CAPTION)
    for episode in analysis.episodes:
        _render_episode(analysis, episode)


def _episode_title(episode: Episode) -> str:
    icon = "🔺" if episode.is_spike else "🔻"
    return (
        f"{icon} {episode.id} · {episode.kind} · {episode.series} · "
        f"{episode.period_label()} · {episode.deviation_pct:+.1f}%"
    )


def _episode_facts(episode: Episode) -> str:
    return (
        f"**Peak day:** {episode.peak_date:%A, %d %b %Y}  \n"
        f"**Peak value:** {episode.peak_value:,.1f} t  \n"
        f"**Expected:** {episode.expected:,.1f} t  \n"
        f"**Deviation:** {episode.deviation_pct:+.1f}%  \n"
        f"**Max |z|:** {episode.max_abs_z:.2f}  \n"
        f"**Detected by:** {', '.join(episode.tests)}"
    )


def _render_episode(analysis: Analysis, episode: Episode) -> None:
    with st.expander(_episode_title(episode)):
        facts, chart = st.columns([1, 2.4], gap="large")
        facts.markdown(_episode_facts(episode))
        window, flags = analysis.episode_context(episode)
        with chart:
            show_chart(
                analysis,
                [episode.series],
                charts.LINE,
                None,
                flagged=flags,
                output=window,
                highlight=(episode.start, episode.end),
                height=EPISODE_CHART_HEIGHT,
                key=f"episode_{episode.id}",
            )
