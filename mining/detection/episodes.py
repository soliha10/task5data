from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .detector import any_test_flagged
from .params import DROP, SPIKE, TESTS

CONTEXT_DAYS = 7
MAX_GAP_DAYS = 1


@dataclass
class Episode:
    id: str
    series: str
    start: pd.Timestamp
    end: pd.Timestamp
    kind: str
    peak_date: pd.Timestamp
    peak_value: float
    expected: float
    deviation_pct: float
    max_abs_z: float
    tests: tuple[str, ...]
    dates: list[pd.Timestamp] = field(default_factory=list)

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def is_spike(self) -> bool:
        return self.kind == SPIKE

    def period_label(self) -> str:
        if self.start == self.end:
            return f"{self.start:%d %b %Y}"
        return f"{self.start:%d %b} – {self.end:%d %b %Y} ({self.days} days)"

    def context_range(self, days: int = CONTEXT_DAYS) -> tuple[pd.Timestamp, pd.Timestamp]:
        margin = pd.Timedelta(days=days)
        return self.start - margin, self.end + margin


def find_episodes(results: dict[str, pd.DataFrame], tests) -> list[Episode]:
    episodes = [
        episode
        for name, result in results.items()
        for episode in _series_episodes(name, result, tests)
    ]
    episodes.sort(key=lambda episode: (episode.start, episode.series))
    for number, episode in enumerate(episodes, 1):
        episode.id = f"A{number:02d}"
    return episodes


def episodes_table(episodes: list[Episode]) -> pd.DataFrame:
    return pd.DataFrame([_episode_row(episode) for episode in episodes])


def _series_episodes(name: str, result: pd.DataFrame, tests) -> list[Episode]:
    flagged = any_test_flagged(result, tests)
    dates = list(result.index[flagged])
    if not dates:
        return []
    return [
        _build_episode(name, result, group, flagged, tests) for group in _group_consecutive(dates)
    ]


def _group_consecutive(dates: list[pd.Timestamp]) -> list[list[pd.Timestamp]]:
    groups = [[dates[0]]]
    for date in dates[1:]:
        if (date - groups[-1][-1]).days <= MAX_GAP_DAYS + 1:
            groups[-1].append(date)
        else:
            groups.append([date])
    return groups


def _context_baseline(adjusted: pd.Series, dates: list[pd.Timestamp], flagged: pd.Series) -> float:
    margin = pd.Timedelta(days=CONTEXT_DAYS)
    in_context = (adjusted.index >= dates[0] - margin) & (adjusted.index <= dates[-1] + margin)
    normal_days = in_context & ~flagged.to_numpy()
    return float(adjusted[normal_days].median() if normal_days.any() else adjusted.median())


def _build_episode(
    name: str, result: pd.DataFrame, dates: list[pd.Timestamp], flagged: pd.Series, tests
) -> Episode:
    group = result.loc[dates]
    peak_date = group["z"].abs().idxmax()
    baseline = _context_baseline(result["adjusted"], dates, flagged)
    peak_value = float(result.at[peak_date, "value"])
    peak_adjusted = float(result.at[peak_date, "adjusted"])
    deviation_pct = (peak_adjusted - baseline) / baseline * 100 if baseline else 0.0

    return Episode(
        id="",
        series=name,
        start=dates[0],
        end=dates[-1],
        kind=SPIKE if deviation_pct >= 0 else DROP,
        peak_date=peak_date,
        peak_value=peak_value,
        expected=peak_value * baseline / peak_adjusted if peak_adjusted else baseline,
        deviation_pct=deviation_pct,
        max_abs_z=float(group["z"].abs().max()),
        tests=tuple(test for test in TESTS if test in tests and group[test].any()),
        dates=dates,
    )


def _episode_row(episode: Episode) -> dict:
    return {
        "ID": episode.id,
        "Series": episode.series,
        "Type": episode.kind,
        "Period": episode.period_label(),
        "Peak date": episode.peak_date.date(),
        "Peak value": episode.peak_value,
        "Expected": episode.expected,
        "Deviation %": episode.deviation_pct,
        "Max |z|": episode.max_abs_z,
        "Detected by": ", ".join(episode.tests),
    }
