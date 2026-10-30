from __future__ import annotations
from datetime import datetime
import streamlit as st
from mining import stats
from mining.analysis import Analysis
from .components import INFO_METRIC

HERO_TEMPLATE = """
<div class="wy-hero">
  <div>
    <div class="wy-brand">WEYLAND-YUTANI CORPORATION</div>
    <div class="wy-title">Mining Operations Analytics</div>
    <div class="wy-sub">{subtitle}</div>
  </div>
  <div class="wy-meta"><span class="wy-badge">● Live from Google Sheets</span><br>
       Last refreshed {refreshed:%H:%M:%S}</div>
</div>
"""

def render_header(analysis: Analysis, fetched_at: datetime) -> None:
    index = analysis.output.index
    subtitle = (
        f"{len(analysis.mines)} mines · {index[0]:%d %b %Y} – {index[-1]:%d %b %Y} · "
        f"{len(index)} days"
    )
    st.markdown(
        HERO_TEMPLATE.format(subtitle=subtitle, refreshed=fetched_at), unsafe_allow_html=True
    )

def render_kpis(analysis: Analysis) -> None:
    top = analysis.top_mine
    top_mean = analysis.summary.at[top, stats.MEAN]
    anomalies = f"{analysis.spike_count} spikes · {analysis.drop_count} drops"
    total, mean, std, best, episodes = st.columns(5)
    total.metric("Total output", f"{analysis.total_stat(stats.TOTAL_OUTPUT):,.0f} t", border=True)
    mean.metric(
        "Mean daily total",
        f"{analysis.total_stat(stats.MEAN):,.1f} t",
        border=True,
        help="Mean of the daily sum over all mines",
    )
    std.metric("Daily std dev (total)", f"{analysis.total_stat(stats.STD):,.1f} t", border=True)
    best.metric("Top mine (mean/day)", top, f"{top_mean:,.1f} t", **INFO_METRIC)
    episodes.metric("Anomaly episodes", len(analysis.episodes), anomalies, **INFO_METRIC)
