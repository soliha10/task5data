from __future__ import annotations

import streamlit as st

from mining.analysis import analyze
from ui.anomalies_tab import render_anomalies_tab
from ui.controls import read_sidebar_controls
from ui.data_source import load_dataset_or_stop
from ui.data_tab import render_data_tab
from ui.header import render_header, render_kpis
from ui.mine_tab import render_mine_tab
from ui.overview_tab import render_overview_tab
from ui.report_panel import render_report_panel
from ui.styles import configure_page


def main() -> None:
    configure_page()
    controls = read_sidebar_controls()
    dataset = load_dataset_or_stop(controls.source)
    analysis = analyze(dataset.output, controls.params, controls.tests)

    render_header(analysis, dataset.fetched_at)
    render_kpis(analysis)

    overview, mines, anomalies, data = st.tabs(
        ["Overview", "Mines", f"Anomalies ({len(analysis.episodes)})", "Data"]
    )
    with overview:
        render_overview_tab(analysis, controls)
    with mines:
        render_mine_tab(analysis, controls)
    with anomalies:
        render_anomalies_tab(analysis)
    with data:
        render_data_tab(dataset.output)

    render_report_panel(analysis, controls, dataset.fetched_at)


main()
