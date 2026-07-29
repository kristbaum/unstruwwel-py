"""Minimal proleptic-Gregorian date arithmetic.

Python's :mod:`datetime` only supports years 1..9999, but historic dates
include year 0 and negative (BC) years.  This module implements a tiny date
type backed by day ordinals (Howard Hinnant's civil-from-days algorithms),
which are valid for any integer year and treat year 0 as a leap year -- the
same proleptic Gregorian calendar that the original R package relied on via
``lubridate``.
"""

from __future__ import annotations

from dataclasses import dataclass


def _is_leap(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _days_in_month(year: int, month: int) -> int:
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month - 1]


def _to_ordinal(year: int, month: int, day: int) -> int:
    y = year - (1 if month <= 2 else 0)
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (month - 3 if month > 2 else month + 9) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _from_ordinal(z: int) -> tuple[int, int, int]:
    z += 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    day = doy - (153 * mp + 2) // 5 + 1
    month = mp + 3 if mp < 10 else mp - 9
    return (y + (1 if month <= 2 else 0), month, day)


@dataclass(frozen=True, order=True)
class Date:
    """A calendar date that allows year 0 and negative years."""

    year: int
    month: int
    day: int

    @classmethod
    def ymd(cls, year: int, month: int = 1, day: int = 1) -> Date:
        return cls(year, month, day)

    @classmethod
    def from_ordinal(cls, ordinal: int) -> Date:
        return cls(*_from_ordinal(ordinal))

    @property
    def ordinal(self) -> int:
        return _to_ordinal(self.year, self.month, self.day)

    def plus_years(self, n: int) -> Date:
        year = self.year + n
        day = min(self.day, _days_in_month(year, self.month))
        return Date(year, self.month, day)

    def plus_months(self, n: int) -> Date:
        total = (self.year * 12 + (self.month - 1)) + n
        year, month = divmod(total, 12)
        month += 1
        day = min(self.day, _days_in_month(year, month))
        return Date(year, month, day)

    def plus_days(self, n: int) -> Date:
        return Date.from_ordinal(self.ordinal + n)

    def with_day(self, day: int) -> Date:
        return Date(self.year, self.month, day)

    def iso(self) -> str:
        if self.year < 0:
            return f"-{abs(self.year):04d}-{self.month:02d}-{self.day:02d}"
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"


@dataclass(frozen=True)
class Interval:
    """A time span delimited by two :class:`Date` endpoints."""

    start: Date
    end: Date

    @classmethod
    def of(cls, a: Date, b: Date) -> Interval:
        return cls(a, b)

    def standardize(self) -> Interval:
        """Return a copy with ``start <= end``."""
        if self.start.ordinal > self.end.ordinal:
            return Interval(self.end, self.start)
        return self
