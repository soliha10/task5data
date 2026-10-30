from __future__ import annotations
import pandas as pd

MEAN, STD, MEDIAN, Q1, Q3, IQR, MIN, MAX, TOTAL_OUTPUT = (
    "Mean",
    "Std dev",
    "Median",
    "Q1",
    "Q3",
    "IQR",
    "Min",
    "Max",
    "Total output",
)
STAT_COLUMNS = [MEAN, STD, MEDIAN, Q1, Q3, IQR, MIN, MAX, TOTAL_OUTPUT]

def describe_series(output: pd.DataFrame) -> pd.DataFrame:
    first_quartile = output.quantile(0.25)
    third_quartile = output.quantile(0.75)
    table = pd.DataFrame(
        {
            MEAN: output.mean(),
            STD: output.std(ddof=1),
            MEDIAN: output.median(),
            Q1: first_quartile,
            Q3: third_quartile,
            IQR: third_quartile - first_quartile,
            MIN: output.min(),
            MAX: output.max(),
            TOTAL_OUTPUT: output.sum(),
        }
    )
    table.index.name = "Series"
    return table[STAT_COLUMNS]
