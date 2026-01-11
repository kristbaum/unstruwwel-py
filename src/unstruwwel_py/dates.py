from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

MONTH_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}


def iso_year(y: int) -> str:
    if y >= 0:
        return f"{y:04d}"
    return f"-{abs(y):04d}"


def iso_date(y: int, m: int, d: int) -> str:
    return f"{iso_year(y)}-{m:02d}-{d:02d}"


@dataclass
class Period:
    start: Tuple[int, int, int]  # (y, m, d)
    end: Tuple[int, int, int]
    fuzzy: int = 0  # -1 approximate, 1 uncertain
    express: int = 0  # -1 before, 1 after

    @property
    def time_span(self) -> Tuple[Optional[float], Optional[float]]:
        sy = self.start[0]
        ey = self.end[0]
        if self.express < 0:
            return (-float("inf"), ey)
        if self.express > 0:
            return (sy, float("inf"))
        return (min(sy, ey), max(sy, ey))

    @property
    def iso_format(self) -> str:
        if self.express < 0:
            # open on the left
            end = iso_date(*self.end)
            return f"..{end}"
        if self.express > 0:
            # open on the right
            start = iso_date(*self.start)
            return f"{start}.."
        a = iso_date(*self.start)
        b = iso_date(*self.end)
        if self.fuzzy < 0:
            a = f"{a}~"
            b = f"{b}~"
        if self.fuzzy > 0:
            a = f"{a}?"
            b = f"{b}?"
        return f"{a}/{b}"


def period_for_year(y: int) -> Period:
    # A full year period
    if y >= 0:
        return Period(start=(y, 1, 1), end=(y, 12, 31))
    else:
        return Period(start=(y, 1, 1), end=(y, 12, 31))


def season_months(name: str) -> List[int]:
    return {
        "spring": [3, 4, 5],
        "summer": [6, 7, 8],
        "autumn": [9, 10, 11],
        "winter": [12, 1, 2],
    }[name]


def period_for_month(y: int, m: int) -> Period:
    return Period(start=(y, m, 1), end=(y, m, MONTH_DAYS[m]))


def period_for_season(y: int, season: str) -> Period:
    months = season_months(season)
    start_m = months[0]
    end_m = months[-1]
    # Handle winter as a cross-year season: Dec of Y through Feb of Y+1
    if season == "winter":
        return Period(start=(y, 12, 1), end=(y + 1, 2, MONTH_DAYS[2]))
    return Period(start=(y, start_m, 1), end=(y, end_m, MONTH_DAYS[end_m]))
