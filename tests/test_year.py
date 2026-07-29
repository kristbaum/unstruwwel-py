import pytest

from unstruwwel import Year
from unstruwwel.dates import Date, Interval
from unstruwwel.periods import YEAR_ZERO


def neg(date, years):
    return date.plus_years(-years)


def test_invalid_year():
    with pytest.raises(ValueError, match="not an integer"):
        Year(197.5)
    with pytest.raises(TypeError, match="not a scalar integer"):
        Year([197, 198])


def test_invalid_take_with_year():
    with pytest.raises(ValueError, match="not a valid month or season"):
        Year(1900).take(type="j")


def test_positive_year():
    assert Year(1750).interval == Interval(Date(1750, 1, 1), Date(1750, 12, 31))
    assert Year(1750).time_span == (1750, 1750)


def test_positive_year_with_month():
    assert Year(1750).take(type="may").interval == Interval(
        Date(1750, 5, 1), Date(1750, 5, 31)
    )
    assert Year(1750).take(type="may").time_span == (1750, 1750)


def test_positive_year_with_month_and_day():
    assert Year(1750).take(5, "april").interval == Interval(
        Date(1750, 4, 5), Date(1750, 4, 5)
    )
    assert Year(1750).take(5, "april").time_span == (1750, 1750)


def test_negative_year():
    assert Year(-1750).interval == Interval(
        neg(YEAR_ZERO, 1750), neg(Date(0, 12, 31), 1750)
    )
    assert Year(-1750).time_span == (-1750, -1750)


def test_negative_year_with_month():
    assert Year(-1750).take(type="may").interval == Interval(
        neg(Date(0, 5, 1), 1750), neg(Date(0, 5, 31), 1750)
    )
    assert Year(-1750).take(type="may").time_span == (-1750, -1750)


def test_negative_year_with_month_and_day():
    assert Year(-1750).take(5, "april").interval == Interval(
        neg(Date(0, 4, 5), 1750), neg(Date(0, 4, 5), 1750)
    )
    assert Year(-1750).take(5, "april").time_span == (-1750, -1750)
