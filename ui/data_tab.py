from __future__ import annotations
import pandas as pd
import streamlit as st
from .components import styled

CSV_FILE_NAME = "mining_output.csv"
TABLE_HEIGHT = 480

def render_data_tab(output: pd.DataFrame) -> None:
    st.dataframe(styled(output), width="stretch", height=TABLE_HEIGHT)
    st.download_button(
        "Download CSV",
        output.to_csv().encode(),
        CSV_FILE_NAME,
        "text/csv",
        icon=":material/download:",
    )
