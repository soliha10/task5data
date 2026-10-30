from __future__ import annotations
import streamlit as st
from mining import brand

PAGE_TITLE = "Weyland-Yutani · Mining Analytics"
PAGE_ICON = "⛏️"
HERO_CSS = f"""
.wy-hero {{display:flex; justify-content:space-between; align-items:flex-end;
          position:relative; padding-bottom:1rem; margin-bottom:1.4rem;}}
.wy-hero::after {{content:""; position:absolute; left:0; right:0; bottom:0; height:3px;
          border-radius:3px;
          background:linear-gradient(90deg, {brand.PRIMARY_600}, {brand.PRIMARY_400} 45%,
                     {brand.BORDER} 100%);}}
.wy-brand {{font-size:.78rem; font-weight:700; letter-spacing:.14em; color:{brand.ACTION};}}
.wy-title {{font-size:2rem; font-weight:700; color:{brand.TEXT}; line-height:1.2;
          margin:.15rem 0; letter-spacing:-.01em;}}
.wy-sub {{color:{brand.TEXT_MUTED}; font-size:.95rem;}}
.wy-meta {{text-align:right; color:{brand.TEXT_MUTED}; font-size:.82rem; line-height:1.6;}}
.wy-badge {{display:inline-block; padding:.15rem .65rem; border-radius:999px; font-size:.75rem;
          font-weight:600; background:{brand.SUBTLE_ACCENT}; color:{brand.PRIMARY_800};}}
"""
LAYOUT_CSS = """
.block-container {padding-top:3.5rem; padding-bottom:3rem; max-width:1400px;}
"""
SIDEBAR_CSS = f"""
section[data-testid="stSidebar"] h3 {{font-size:.75rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.1em; color:{brand.PRIMARY_800}; margin-top:1.4rem;}}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stSliderTickBar"] {{
  color:{brand.TEXT_MUTED_ON_TINT};}}
"""
METRIC_CSS = f"""
div[data-testid="stMetric"] {{background:{brand.WHITE}; border:1px solid {brand.BORDER};
  border-radius:{brand.RADIUS_PX}px;
  box-shadow:inset {brand.ACCENT_BAR_PX}px 0 0 {brand.ACTION}, {brand.SHADOW_SOFT};
  transition:box-shadow .15s ease, transform .15s ease;}}
div[data-testid="stMetric"]:hover {{transform:translateY(-1px);
  box-shadow:inset {brand.ACCENT_BAR_PX}px 0 0 {brand.ACTION}, {brand.SHADOW_RAISED};}}
[data-testid="stMetricValue"] {{color:{brand.TEXT}; font-variant-numeric:tabular-nums;}}
[data-testid="stMetricLabel"] {{color:{brand.TEXT_MUTED};}}
"""
TABS_CSS = f"""
[data-testid="stTab"] {{color:{brand.TEXT_MUTED};}}
[data-testid="stTab"][aria-selected="true"] {{color:{brand.ACTION}; font-weight:600;}}
"""
BUTTONS_CSS = f"""
button[data-testid="stBaseButton-primary"] {{background:{brand.ACTION};
  border-color:{brand.ACTION}; color:{brand.WHITE}; font-weight:600;}}
button[data-testid="stBaseButton-primary"]:hover {{background:{brand.ACTION_HOVER};
  border-color:{brand.ACTION_HOVER}; color:{brand.WHITE};}}
button[data-testid="stBaseButton-secondary"] {{background:{brand.WHITE};
  border-color:{brand.ACTION}; color:{brand.ACTION}; font-weight:600;}}
button[data-testid="stBaseButton-secondary"]:hover {{background:{brand.SUBTLE_BACKGROUND};
  border-color:{brand.ACTION_HOVER}; color:{brand.ACTION_HOVER};}}
"""
CONTAINERS_CSS = f"""
div[data-testid="stExpander"] details {{border:1px solid {brand.BORDER};
  border-radius:{brand.RADIUS_PX}px; box-shadow:{brand.SHADOW_SOFT};}}
div[data-testid="stExpander"] summary:hover {{color:{brand.ACTION};
  background:{brand.SUBTLE_BACKGROUND};}}
div[data-testid="stDataFrame"] {{border-radius:{brand.RADIUS_SMALL_PX}px;
  font-variant-numeric:tabular-nums;}}
"""
PAGE_CSS = "".join(
    (LAYOUT_CSS, HERO_CSS, SIDEBAR_CSS, METRIC_CSS, TABS_CSS, BUTTONS_CSS, CONTAINERS_CSS)
)

def configure_page() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="expanded"
    )
    st.markdown(f"<style>{PAGE_CSS}</style>", unsafe_allow_html=True)

def sidebar_heading(text: str) -> None:
    st.markdown(f"### {text}")
