from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import streamlit as st
from mining.analysis import Analysis
from mining.data import extract_sheet_id, sheet_csv_url
from mining.report import ReportSettings, build_report
from .controls import Controls
from .styles import sidebar_heading

STATE_KEY = "pdf_report"
FILE_NAME_TEMPLATE = "weyland-yutani-mining-report-{:%Y%m%d-%H%M}.pdf"

@dataclass(frozen=True)
class GeneratedReport:
    fingerprint: tuple
    content: bytes
    file_name: str

def render_report_panel(analysis: Analysis, controls: Controls, fetched_at: datetime) -> None:
    fingerprint = (fetched_at, controls)
    with st.sidebar:
        sidebar_heading("Report")
        if st.button("Generate PDF report", icon=":material/picture_as_pdf:", width="stretch"):
            with st.spinner("Building PDF report…"):
                st.session_state[STATE_KEY] = _generate(analysis, controls, fingerprint)
        _offer_download(st.session_state.get(STATE_KEY), fingerprint, len(analysis.episodes))

def _generate(analysis: Analysis, controls: Controls, fingerprint: tuple) -> GeneratedReport:
    now = datetime.now()
    settings = ReportSettings(
        source_url=sheet_csv_url(extract_sheet_id(controls.source)),
        chart_kind=controls.chart_kind,
        trend_degree=controls.trend_degree,
        generated_at=now,
    )
    return GeneratedReport(
        fingerprint, build_report(analysis, settings), FILE_NAME_TEMPLATE.format(now)
    )

def _offer_download(report: GeneratedReport | None, fingerprint: tuple, episodes: int) -> None:
    if report is None or report.fingerprint != fingerprint:
        return
    st.download_button(
        "Download PDF",
        report.content,
        report.file_name,
        "application/pdf",
        type="primary",
        icon=":material/download:",
        width="stretch",
    )
    st.caption(f"{len(report.content) / 1024:,.0f} KB · {episodes} anomaly sections")
