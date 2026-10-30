from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import streamlit as st

from mining.data import DEFAULT_SHEET_ID, load_mine_output

SHEET_URL_SETTING = "SHEET_URL"
CACHE_TTL_SECONDS = 60


@dataclass(frozen=True)
class Dataset:
    output: pd.DataFrame
    fetched_at: datetime


def default_source() -> str:
    fallback = os.environ.get(SHEET_URL_SETTING, DEFAULT_SHEET_ID)
    try:
        return st.secrets.get(SHEET_URL_SETTING, "") or fallback
    except Exception:
        return fallback


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Loading data from the generator spreadsheet…")
def load_dataset(source: str) -> Dataset:
    return Dataset(load_mine_output(source), datetime.now())


def refresh_dataset() -> None:
    load_dataset.clear()


def load_dataset_or_stop(source: str) -> Dataset:
    try:
        return load_dataset(source)
    except Exception as error:
        st.error(f"Could not load data from the spreadsheet: {error}")
        st.stop()
