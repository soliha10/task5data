from __future__ import annotations
import io
import re
import pandas as pd
import requests

DEFAULT_SHEET_ID = "11bMcCAMNjKuTDoMHstHA9hZesTna60EVzw3Xp0Xsx5Q"
DATA_SHEET = "Data"
DATE_COLUMN = "Date"
TOTAL = "Total"
TOTAL_LABEL = "Total (all mines)"
SHEET_DATE_FORMAT = "%m/%d/%Y"
REQUEST_TIMEOUT_SECONDS = 20

def extract_sheet_id(source: str) -> str:
    match = re.search(r"/d/([A-Za-z0-9_-]+)", source)
    return match.group(1) if match else source.strip()

def sheet_csv_url(sheet_id: str, sheet: str = DATA_SHEET) -> str:
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    return f"{base}/gviz/tq?tqx=out:csv&sheet={sheet}"

def download_csv(url: str) -> str:
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    if "text/csv" not in response.headers.get("content-type", ""):
        raise ValueError(
            "The spreadsheet did not return CSV. Make sure it is shared as 'Anyone with the link'."
        )
    return response.text

def parse_mine_output(csv_text: str) -> pd.DataFrame:
    raw = pd.read_csv(io.StringIO(csv_text), dtype=str)
    raw.columns = [str(name).strip() for name in raw.columns]
    if DATE_COLUMN not in raw.columns:
        raise ValueError(f"The {DATA_SHEET} sheet has no '{DATE_COLUMN}' column.")
    output = raw[[DATE_COLUMN, *_mine_names(raw.columns)]].copy()
    output[DATE_COLUMN] = _parse_dates(output[DATE_COLUMN])
    output = output.dropna(subset=[DATE_COLUMN]).set_index(DATE_COLUMN).sort_index()
    output = output.apply(pd.to_numeric, errors="coerce")
    output = output.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if output.empty:
        raise ValueError(f"The {DATA_SHEET} sheet contains no numeric mine output.")
    output = output.fillna(0.0)
    output[TOTAL] = output.sum(axis=1)
    return output

def load_mine_output(source: str) -> pd.DataFrame:
    return parse_mine_output(download_csv(sheet_csv_url(extract_sheet_id(source))))

def mine_columns(output: pd.DataFrame) -> list[str]:
    return [name for name in output.columns if name != TOTAL]

def series_label(name: str) -> str:
    return TOTAL_LABEL if name == TOTAL else name

def _mine_names(columns) -> list[str]:
    excluded = {DATE_COLUMN, TOTAL}
    return [
        name for name in columns if name and name not in excluded and not name.startswith("Unnamed")
    ]

def _parse_dates(values: pd.Series) -> pd.Series:
    dates = pd.to_datetime(values, format=SHEET_DATE_FORMAT, errors="coerce")
    if dates.isna().all():
        dates = pd.to_datetime(values, errors="coerce")
    return dates
