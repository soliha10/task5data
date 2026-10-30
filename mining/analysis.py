from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from .data import TOTAL, mine_columns
from .detection import (
    DetectionParams,
    Episode,
    count_flags_by_test,
    detect_all,
    find_episodes,
    flagged_days,
)
from .stats import MEAN, describe_series

FlagMap = dict[str, pd.DataFrame]

@dataclass(frozen=True)
class Analysis:
    output: pd.DataFrame
    summary: pd.DataFrame
    results: dict[str, pd.DataFrame]
    flagged: FlagMap
    episodes: list[Episode]
    flag_counts: pd.DataFrame
    params: DetectionParams
    tests: tuple[str, ...]
    @property
    def mines(self) -> list[str]:
        return mine_columns(self.output)
    @property
    def top_mine(self) -> str:
        return self.summary.loc[self.mines, MEAN].idxmax()
    @property
    def spike_count(self) -> int:
        return sum(episode.is_spike for episode in self.episodes)
    @property
    def drop_count(self) -> int:
        return len(self.episodes) - self.spike_count
    def total_stat(self, column: str) -> float:
        return float(self.summary.at[TOTAL, column])
    def episodes_of(self, series: str) -> list[Episode]:
        return [episode for episode in self.episodes if episode.series == series]
    def flags_of(self, series: str) -> FlagMap:
        return {series: self.flagged[series]}
    def episode_context(self, episode: Episode) -> tuple[pd.DataFrame, FlagMap]:
        start, end = episode.context_range()
        window = self.output.loc[start:end, [episode.series]]
        return window, {episode.series: self.flagged[episode.series].loc[start:end]}

def analyze(output: pd.DataFrame, params: DetectionParams, tests: tuple[str, ...]) -> Analysis:
    results = detect_all(output, params)
    return Analysis(
        output=output,
        summary=describe_series(output),
        results=results,
        flagged={name: flagged_days(result, tests) for name, result in results.items()},
        episodes=find_episodes(results, tests),
        flag_counts=count_flags_by_test(results, tests),
        params=params,
        tests=tests,
    )
