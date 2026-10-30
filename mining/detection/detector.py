from __future__ import annotations
import numpy as np
import pandas as pd
from .outlier_tests import (
    grubbs_outliers,
    iqr_outliers,
    neighbour_moving_average,
    remove_trend_and_weekday,
    z_scores,
)
from .params import DROP, GRUBBS, IQR, MOVING_AVG, SPIKE, TESTS, ZSCORE, DetectionParams

ANY_SELECTED = "Any selected"
FLAGGED_COLUMNS = ["value", "z", "ma_dev_pct", "direction", "tests"]

def detect_outliers(series: pd.Series, params: DetectionParams) -> pd.DataFrame:
    tested = remove_trend_and_weekday(series) if params.adjust else series.astype(float)
    scores = z_scores(tested)
    average, deviation_pct = neighbour_moving_average(tested, params.ma_window)
    return pd.DataFrame(
        {
            "value": series.astype(float),
            "adjusted": tested,
            "z": scores,
            "ma": average,
            "ma_dev_pct": deviation_pct,
            "direction": np.where(tested >= tested.median(), SPIKE, DROP),
            IQR: iqr_outliers(tested, params.iqr_k),
            ZSCORE: scores.abs() > params.z_threshold,
            MOVING_AVG: (deviation_pct.abs() > params.ma_pct).fillna(False).astype(bool),
            GRUBBS: grubbs_outliers(tested, params.grubbs_alpha),
        }
    )

def detect_all(output: pd.DataFrame, params: DetectionParams) -> dict[str, pd.DataFrame]:
    return {name: detect_outliers(output[name], params) for name in output.columns}

def any_test_flagged(result: pd.DataFrame, tests) -> pd.Series:
    tests = list(tests)
    if not tests:
        return pd.Series(False, index=result.index)
    return result[tests].any(axis=1)

def flagged_days(result: pd.DataFrame, tests) -> pd.DataFrame:
    tests = list(tests)
    flagged = result[any_test_flagged(result, tests)].copy()
    flagged["tests"] = [
        ", ".join(test for test in tests if row[test]) for _, row in flagged.iterrows()
    ]
    return flagged[FLAGGED_COLUMNS]

def count_flags_by_test(results: dict[str, pd.DataFrame], tests) -> pd.DataFrame:
    rows = {name: _flag_counts(result, tests) for name, result in results.items()}
    table = pd.DataFrame.from_dict(rows, orient="index")
    table.index.name = "Series"
    return table

def _flag_counts(result: pd.DataFrame, tests) -> dict[str, int]:
    counts = {test: int(result[test].sum()) for test in TESTS}
    counts[ANY_SELECTED] = int(any_test_flagged(result, tests).sum())
    return counts
