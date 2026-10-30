from __future__ import annotations
from dataclasses import dataclass

IQR, ZSCORE, MOVING_AVG, GRUBBS = "IQR", "Z-score", "Moving avg", "Grubbs"
TESTS = (IQR, ZSCORE, MOVING_AVG, GRUBBS)
SPIKE, DROP = "Spike", "Drop"

@dataclass(frozen=True)
class DetectionParams:
    iqr_k: float = 1.5
    z_threshold: float = 2.5
    ma_window: int = 7
    ma_pct: float = 30.0
    grubbs_alpha: float = 0.05
    adjust: bool = True
