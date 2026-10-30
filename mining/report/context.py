from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from ..analysis import Analysis
from ..charts import ColorMap, FlagMap, render_png, series_colors, single_series_kind

@dataclass(frozen=True)
class ReportSettings:
    source_url: str
    chart_kind: str
    trend_degree: int | None
    generated_at: datetime

@dataclass(frozen=True)
class ReportContext:
    analysis: Analysis
    settings: ReportSettings
    colors: ColorMap
    @classmethod
    def create(cls, analysis: Analysis, settings: ReportSettings) -> ReportContext:
        return cls(analysis, settings, series_colors(analysis.output.columns))
    @property
    def single_series_kind(self) -> str:
        return single_series_kind(self.settings.chart_kind)
    def chart_png(
        self,
        series: list[str],
        kind: str,
        flagged: FlagMap,
        *,
        output: pd.DataFrame | None = None,
        with_trend: bool = True,
        **options,
    ) -> bytes:
        return render_png(
            self.analysis.output if output is None else output,
            series,
            kind,
            self.settings.trend_degree if with_trend else None,
            flagged,
            self.colors,
            **options,
        )
