"""Time-period objects that map verbal specifications to date intervals.

These mirror the R6 classes of the original R package: :class:`Periods` is the
base type holding an interval, while :class:`Century`, :class:`Decade`, and
:class:`Year` know how to build their interval from a numeric value and how to
narrow it down via :meth:`take` (e.g. "first half", "last third", "early").
"""

from __future__ import annotations

import datetime
import math

from .dates import Date, Interval

YEAR_ZERO = Date(0, 1, 1)
_INFINITY_YEARS = 9999

MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)
SEASONS = {
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "autumn": [9, 10, 11],
    "winter": [12, 13, 14],
}
#: Parts a :meth:`Periods.take` can narrow down to; ``None`` means an equal tenth.
TAKE_TYPES = ("early", "mid", "late", "half", "third", "quarter")


def current_year() -> int:
    return datetime.datetime.now().astimezone().year


def _is_negative(interval: Interval) -> bool:
    return interval.start.ordinal < YEAR_ZERO.ordinal


class Periods:
    """A time period delimited by an interval, with fuzzy/express flags."""

    def __init__(self, interval: Interval | None = None, parts=None):
        #: ``-1`` approximate, ``1`` uncertain, ``0`` exact.
        self.fuzzy = 0
        #: ``-1`` before, ``1`` after, ``0`` neither.
        self.express = 0

        if interval is not None:
            self._interval = interval
            return

        items = [p for p in _flatten(parts) if p is not None]
        intervals = []
        fuzzies = []
        for item in items:
            if isinstance(item, Periods):
                intervals.append(item.interval)
                fuzzies.append(item.fuzzy)
            else:
                intervals.append(Year(item).interval)
        if not intervals:
            raise ValueError("at least one valid period is required")

        start = min((iv.start for iv in intervals), key=lambda d: d.ordinal)
        end = max((iv.end for iv in intervals), key=lambda d: d.ordinal)
        self._interval = Interval(start, end)

        if any(f < 0 for f in fuzzies):
            self.fuzzy = -1
        if any(f > 0 for f in fuzzies):
            self.fuzzy = 1

    # -- conversions ---------------------------------------------------------
    @property
    def interval(self) -> Interval:
        iv = self._interval.standardize()
        if self.express < 0:
            iv = Interval(
                YEAR_ZERO.plus_years(-_INFINITY_YEARS), iv.start.plus_days(-1)
            )
        elif self.express > 0:
            iv = Interval(iv.end.plus_days(1), YEAR_ZERO.plus_years(_INFINITY_YEARS))
        return iv

    @property
    def time_span(self):
        iv = self.interval
        a, b = iv.start.year, iv.end.year
        if a == -_INFINITY_YEARS:
            a = -math.inf
        if b == _INFINITY_YEARS:
            b = math.inf
        return tuple(sorted((a, b)))

    @property
    def iso_format(self) -> str:
        iv = self.interval
        parts = [iv.start.iso(), iv.end.iso()]
        if self.fuzzy < 0:
            parts = [p + "~" for p in parts]
        if self.fuzzy > 0:
            parts = [p + "?" for p in parts]
        if iv.start.year == -_INFINITY_YEARS:
            return ".." + parts[1]
        if iv.end.year == _INFINITY_YEARS:
            return parts[0] + ".."
        return "/".join(parts)

    # -- specification -------------------------------------------------------
    def set_additions(self, tokens) -> Periods:
        tokens = list(tokens)
        if any(t in ("approximate", "?") for t in tokens):
            self.fuzzy = -1
        if "uncertain" in tokens:
            self.fuzzy = 1
        if "before" in tokens:
            self.express = -1
        if "after" in tokens:
            self.express = 1
        return self

    def take(self, x=None, type=None, ignore_errors=False) -> Periods:
        try:
            if isinstance(x, (list, tuple)) and len(x) == 2:
                x, type = x[0], x[1]
            if x is not None and x != "last" and x != "first":
                x = _as_numeric(x)
            if type is not None and str(type).lower() not in TAKE_TYPES:
                raise ValueError(f"`{type}` is not a valid type")
            type = str(type).lower()

            if type == "early":
                iv = self._take_early()
            elif type == "late":
                iv = self._take_late()
            elif type == "mid":
                iv = self._take_mid()
            else:
                iv = self._take_period(x, type)

            result = Periods(interval=iv)
            result.fuzzy = self.fuzzy
            result.express = self.express
            return result
        except Exception:
            if ignore_errors:
                return self
            raise

    def _take_period(self, value, type) -> Interval:
        max_value = {"quarter": 4, "third": 3, "half": 2}.get(type, 10)
        if value == "last":
            value = max_value
        elif value == "first":
            value = 1
        value = int(value)
        if not 1 <= value <= max_value:
            raise ValueError(f"`{value}` is out of range for `{type}`")

        iv = self._interval.standardize()
        n_years = abs(iv.end.year - iv.start.year) + 1
        step = round(n_years / max_value)

        if _is_negative(iv):
            upper = iv.end.plus_years(-(value - 1) * step)
            lower = iv.end.plus_years(-(value * step - 2)).plus_days(-1)
            if value == max_value and step % 3 == 0:
                lower = lower.plus_years(-1)
            return Interval(lower, upper)

        lower = iv.start.plus_years((value - 1) * step)
        upper = iv.start.plus_years(value * step).plus_days(-1)
        if value == max_value and step % 3 == 0:
            upper = upper.plus_years(1)
        return Interval(lower, upper)

    def _take_early(self) -> Interval:
        raise NotImplementedError("`early` is not supported for this period")

    def _take_mid(self) -> Interval:
        raise NotImplementedError("`mid` is not supported for this period")

    def _take_late(self) -> Interval:
        raise NotImplementedError("`late` is not supported for this period")


class Century(Periods):
    def __init__(self, value):
        super().__init__(interval=Interval(YEAR_ZERO, YEAR_ZERO))
        value = _as_integer(value)
        if not (abs(value) < 100 and value < 22):
            raise ValueError(f"`{value}` is not a valid century")

        if value < 0:
            years = abs(value + 1) * 100 + 1
            start = YEAR_ZERO.plus_years(-years)
            iv = Interval(start, start.plus_years(-98).plus_days(-1))
        else:
            start = Date((value - 1) * 100 + 1, 1, 1)
            iv = Interval(start, start.plus_years(100).plus_days(-1))
        self._interval = iv.standardize()

    def _take_early(self) -> Interval:
        iv = self._interval.standardize()
        if _is_negative(iv):
            return Interval(iv.start.plus_years(85), iv.end)
        return Interval(iv.start, iv.end.plus_years(-85))

    def _take_mid(self) -> Interval:
        iv = self._interval.standardize()
        return Interval(iv.start.plus_years(45), iv.end.plus_years(-45))

    def _take_late(self) -> Interval:
        iv = self._interval.standardize()
        if _is_negative(iv):
            return Interval(iv.start, iv.end.plus_years(-85))
        return Interval(iv.start.plus_years(85), iv.end)


class Decade(Periods):
    def __init__(self, value, official_def=False):
        super().__init__(interval=Interval(YEAR_ZERO, YEAR_ZERO))
        value = _as_integer(value)
        if not (value <= current_year() and value % 10 == 0):
            raise ValueError(f"`{value}` is not a valid decade")

        if value < 0:
            start = YEAR_ZERO.plus_years(-abs(value))
            if official_def:
                start = start.plus_years(-1)
            iv = Interval(start, start.plus_years(-8).plus_days(-1))
        else:
            start = Date(value, 1, 1)
            if official_def:
                start = start.plus_years(1)
            iv = Interval(start, start.plus_years(10).plus_days(-1))
        self._interval = iv.standardize()

    def _take_early(self) -> Interval:
        iv = self._interval.standardize()
        if _is_negative(iv):
            return Interval(iv.start.plus_years(8), iv.end)
        return Interval(iv.start, iv.end.plus_years(-8))

    def _take_mid(self) -> Interval:
        iv = self._interval.standardize()
        return Interval(iv.start.plus_years(4), iv.end.plus_years(-4))

    def _take_late(self) -> Interval:
        iv = self._interval.standardize()
        if _is_negative(iv):
            return Interval(iv.start, iv.end.plus_years(-8))
        return Interval(iv.start.plus_years(8), iv.end)


class Year(Periods):
    def __init__(self, value):
        super().__init__(interval=Interval(YEAR_ZERO, YEAR_ZERO))
        value = _as_integer(value)
        if value > current_year():
            raise ValueError(f"`{value}` is not a valid year")

        if value < 0:
            start = YEAR_ZERO.plus_years(-abs(value))
        else:
            start = Date(value, 1, 1)
        iv = Interval(start, start.plus_years(1).plus_days(-1))
        self._interval = iv.standardize()

    def take(self, x=None, type=None, ignore_errors=False) -> Periods:
        try:
            if isinstance(x, (list, tuple)) and len(x) == 2:
                x, type = x[0], x[1]
            if x is not None:
                x = _as_numeric(x)
            type = str(type).lower()

            if type in MONTHS:
                months = [MONTHS.index(type) + 1]
            elif type in SEASONS:
                months = SEASONS[type]
            else:
                raise ValueError(f"`{type}` is not a valid month or season")

            iv = self._take_months(x, months)
            result = Periods(interval=iv)
            result.fuzzy = self.fuzzy
            result.express = self.express
            return result
        except Exception:
            if ignore_errors:
                return self
            raise

    def _take_months(self, value, months) -> Interval:
        """Narrow to ``months`` of this year, optionally to a single day."""
        start = self._interval.standardize().start
        lower = start.plus_months(min(months) - 1)
        upper = start.plus_months(max(months)).plus_days(-1)
        if value is not None and len(months) == 1 and 1 <= value <= upper.day:
            lower = lower.with_day(int(value))
            upper = upper.with_day(int(value))
        return Interval(lower, upper)


def _as_numeric(value):
    """Coerce to ``float`` like R's ``as.numeric``; non-numeric becomes ``None``."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(result) else result


def _as_integer(value) -> int:
    if isinstance(value, str):
        value = float(value)
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"`{value}` is not an integer")
        value = int(value)
    if not isinstance(value, int):
        raise TypeError(f"`{value}` is not a scalar integer")
    return value


def _flatten(items):
    if items is None:
        return
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        else:
            yield item
