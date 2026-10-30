from __future__ import annotations
from dataclasses import dataclass
import streamlit as st
from mining import charts
from mining.detection import TESTS, DetectionParams
from .data_source import default_source, refresh_dataset
from .styles import sidebar_heading

TREND_OPTIONS = {
    "None": None,
    "Linear (1)": 1,
    "Quadratic (2)": 2,
    "Cubic (3)": 3,
    "Quartic (4)": 4,
}
DEFAULT_TREND = "Quadratic (2)"
GRUBBS_ALPHAS = [0.001, 0.01, 0.025, 0.05, 0.1]
DEFAULTS = DetectionParams()
ADJUST_HELP = (
    "Divides each series by its linear trend and median weekday factor, so regular "
    "weekend dips and growth are not reported as anomalies."
)

@dataclass(frozen=True)
class Controls:
    source: str
    chart_kind: str
    trend_degree: int | None
    tests: tuple[str, ...]
    params: DetectionParams
    @property
    def single_series_kind(self) -> str:
        return charts.single_series_kind(self.chart_kind)

def read_sidebar_controls() -> Controls:
    with st.sidebar:
        source = _read_source()
        chart_kind, trend_degree, tests = _read_chart_options()
        params = _read_detection_params()
    return Controls(source, chart_kind, trend_degree, tests, params)

def _read_source() -> str:
    sidebar_heading("Data source")
    source = st.text_input("Generator spreadsheet (URL or ID)", value=default_source())
    if st.button("Refresh data", icon=":material/refresh:", type="primary", width="stretch"):
        refresh_dataset()
    return source

def _read_chart_options() -> tuple[str, int | None, tuple[str, ...]]:
    sidebar_heading("Charts")
    kind = st.segmented_control("Chart type", charts.KINDS, default=charts.LINE, required=True)
    trend = st.selectbox(
        "Trendline (polynomial)",
        list(TREND_OPTIONS),
        index=list(TREND_OPTIONS).index(DEFAULT_TREND),
    )
    tests = st.multiselect("Highlight outliers found by", TESTS, default=list(TESTS))
    return kind, TREND_OPTIONS[trend], tuple(tests)

def _read_detection_params() -> DetectionParams:
    sidebar_heading("Anomaly tests")
    return DetectionParams(
        iqr_k=st.slider("IQR rule · multiplier k", 0.5, 4.0, DEFAULTS.iqr_k, 0.1),
        z_threshold=st.slider("Z-score · threshold |z|", 1.0, 5.0, DEFAULTS.z_threshold, 0.1),
        ma_window=st.slider("Moving average · window (days)", 3, 21, DEFAULTS.ma_window, 1),
        ma_pct=float(
            st.slider("Moving average · max distance (%)", 5, 100, int(DEFAULTS.ma_pct), 5)
        ),
        grubbs_alpha=st.select_slider(
            "Grubbs · significance α", GRUBBS_ALPHAS, value=DEFAULTS.grubbs_alpha
        ),
        adjust=st.toggle(
            "Remove trend & weekday pattern before testing", value=DEFAULTS.adjust, help=ADJUST_HELP
        ),
    )
