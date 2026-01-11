from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Union


DateSpan = Tuple[Optional[int], Optional[int]]


class PeriodError(ValueError):
    pass


@dataclass(frozen=True)
class Periods:
    """Immutable container for period interval data."""

    interval: Tuple[str, str]
    iso_format: Optional[str] = field(default=None)
    time_span: DateSpan = field(default=(None, None))


@dataclass
class Year:
    year: int

    def __post_init__(self):
        if not isinstance(self.year, int):
            raise ValueError("Year must be integer")
        self.interval = ("", "")
        self.time_span = (self.year, self.year)

    def take(self, day: Optional[int] = None, type: Optional[str] = None):
        if type not in {
            None,
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
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        }:
            raise ValueError("invalid type for Year.take")
        return self


@dataclass
class Decade:
    decade: int

    def __post_init__(self):
        if (
            not isinstance(self.decade, int)
            or abs(self.decade) % 10 != 0
            or abs(self.decade) < 100
        ):
            raise ValueError("Invalid decade")
        self.interval = ("", "")
        self.time_span = (
            self.decade if self.decade >= 0 else -(abs(self.decade) + 9),
            self.decade + 9 if self.decade >= 0 else -abs(self.decade),
        )

    def take(
        self,
        part: Optional[Union[int, str, Tuple[int, str]]] = None,
        type: Optional[str] = None,
        ignore_errors: bool = False,
    ):  # noqa: A003
        valid_types = {None, "half", "third", "quarter", "early", "mid", "late"}
        if isinstance(part, tuple):
            # allow d.take((1, "half")) style
            if (
                len(part) != 2
                or not isinstance(part[0], int)
                or not isinstance(part[1], str)
            ):
                if ignore_errors:
                    return self
                raise ValueError("invalid (part, type) tuple")
            if type is not None and type != part[1]:
                if ignore_errors:
                    return self
                raise ValueError("conflicting type values")
            type = part[1]
            part = part[0]
        # allow 'last' for fractional types
        if isinstance(part, str):
            if type == "half" and part == "last":
                part = 2
            elif type == "third" and part == "last":
                part = 3
            elif type == "quarter" and part == "last":
                part = 4
            else:
                if ignore_errors:
                    return self
                raise ValueError("invalid string part")
        if type not in valid_types:
            if ignore_errors:
                return self
            raise ValueError("invalid take type")
        # If only a numeric part was provided, try to infer a sensible default type
        if part is not None and type is None:
            if isinstance(part, int):
                if part in {1, 2, 3}:
                    type = "third"
                elif part == 4:
                    type = "quarter"
                else:
                    if ignore_errors:
                        return self
                    raise ValueError("invalid part without type")
            else:
                if ignore_errors:
                    return self
                raise ValueError("part provided without type")
        if part is not None and (
            (type == "half" and part not in {1, 2})
            or (type == "third" and part not in {1, 2, 3})
            or (type == "quarter" and part not in {1, 2, 3, 4})
        ):
            if ignore_errors:
                return self
            raise ValueError("invalid part for type")
        # Compute spans
        start_y = self.decade if self.decade >= 0 else -(abs(self.decade) + 9)
        end_y = self.decade + 9 if self.decade >= 0 else -abs(self.decade)

        def set_span(a: int, b: int):
            self.time_span = (min(a, b), max(a, b))

        if type == "early":
            set_span(start_y, start_y + 2)
        elif type == "mid":
            set_span(start_y + 3, start_y + 6)
        elif type == "late":
            set_span(start_y + 7, end_y)
        elif type == "half":
            if part == 1:
                set_span(start_y, start_y + 4)
            elif part == 2:
                set_span(start_y + 5, end_y)
        elif type == "third":
            if part == 1:
                set_span(start_y, start_y + 2)
            elif part == 2:
                set_span(start_y + 3, start_y + 5)
            elif part == 3:
                set_span(start_y + 6, start_y + 8)
        elif type == "quarter":
            if part == 1:
                set_span(start_y, start_y + 2)
            elif part == 2:
                set_span(start_y + 3, start_y + 5)
            elif part == 3:
                set_span(start_y + 6, start_y + 7)
            elif part == 4:
                set_span(start_y + 8, end_y)
        return self


@dataclass
class Century:
    century: int | str

    def __post_init__(self):
        if isinstance(self.century, str):
            try:
                self.century = int(self.century)
            except Exception as e:
                raise ValueError("Invalid century") from e
        if (
            not isinstance(self.century, int)
            or self.century == 0
            or abs(self.century) > 21
        ):
            raise ValueError("Invalid century")
        self.interval = ("", "")
        pos = self.century > 0
        if pos:
            self.time_span = (100 * self.century - 99, 100 * self.century)
        else:
            self.time_span = (-100 * abs(self.century), -100 * abs(self.century) + 99)

    def take(
        self,
        part: Optional[Union[int, str, Tuple[int, str]]] = None,
        type: Optional[str] = None,
        ignore_errors: bool = False,
    ):  # noqa: A003
        valid_types = {None, "half", "third", "quarter", "early", "mid", "late"}
        if isinstance(part, tuple):
            # allow c.take((1, "half")) style
            if (
                len(part) != 2
                or not isinstance(part[0], int)
                or not isinstance(part[1], str)
            ):
                if ignore_errors:
                    return self
                raise ValueError("invalid (part, type) tuple")
            if type is not None and type != part[1]:
                if ignore_errors:
                    return self
                raise ValueError("conflicting type values")
            type = part[1]
            part = part[0]
        # allow 'last' for fractional types
        if isinstance(part, str):
            if type == "half" and part == "last":
                part = 2
            elif type == "third" and part == "last":
                part = 3
            elif type == "quarter" and part == "last":
                part = 4
            else:
                if ignore_errors:
                    return self
                raise ValueError("invalid string part")
        if type not in valid_types:
            if ignore_errors:
                return self
            raise ValueError("invalid take type")
        # If only a numeric part was provided, try to infer a sensible default type
        if part is not None and type is None:
            if isinstance(part, int):
                if part in {1, 2, 3}:
                    type = "third"
                elif part == 4:
                    type = "quarter"
                else:
                    if ignore_errors:
                        return self
                    raise ValueError("invalid part without type")
            else:
                if ignore_errors:
                    return self
                raise ValueError("part provided without type")
        if part is not None and (
            (type == "half" and part not in {1, 2})
            or (type == "third" and part not in {1, 2, 3})
            or (type == "quarter" and part not in {1, 2, 3, 4})
        ):
            if ignore_errors:
                return self
            raise ValueError("invalid part for type")
        # Compute spans
        start_y, end_y = self.time_span  # type: ignore[assignment]
        assert start_y is not None and end_y is not None

        def set_span(a: int, b: int):
            self.time_span = (min(a, b), max(a, b))

        if type == "early":
            # first third roughly
            set_span(int(start_y), int(start_y) + 32)
        elif type == "mid":
            set_span(int(start_y) + 33, int(start_y) + 66)
        elif type == "late":
            set_span(int(start_y) + 67, int(end_y))
        elif type == "half":
            if part == 1:
                set_span(int(start_y), int(start_y) + 49)
            elif part == 2:
                set_span(int(start_y) + 50, int(end_y))
        elif type == "third":
            if part == 1:
                set_span(int(start_y), int(start_y) + 32)
            elif part == 2:
                set_span(int(start_y) + 33, int(start_y) + 65)
            elif part == 3:
                set_span(int(start_y) + 66, int(end_y))
        elif type == "quarter":
            if part == 1:
                set_span(int(start_y), int(start_y) + 24)
            elif part == 2:
                set_span(int(start_y) + 25, int(start_y) + 49)
            elif part == 3:
                set_span(int(start_y) + 50, int(start_y) + 74)
            elif part == 4:
                set_span(int(start_y) + 75, int(end_y))
        return self
