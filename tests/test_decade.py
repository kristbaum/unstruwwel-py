import pytest

from unstruwwel import Decade
from unstruwwel.dates import Date, Interval
from unstruwwel.periods import YEAR_ZERO


def neg(date, years):
    return date.plus_years(-years)


def test_invalid_decade():
    with pytest.raises(ValueError, match="not a valid decade"):
        Decade(203)
    with pytest.raises(ValueError, match="not a valid decade"):
        Decade(2021)
    with pytest.raises(ValueError, match="not an integer"):
        Decade(197.5)
    with pytest.raises(TypeError, match="not a scalar integer"):
        Decade([197, 198])


def test_positive_decade():
    assert Decade(1770).interval == Interval(Date(1770, 1, 1), Date(1779, 12, 31))
    assert Decade(1770).time_span == (1770, 1779)

    assert Decade(1950, official_def=True).interval == Interval(
        Date(1951, 1, 1), Date(1960, 12, 31)
    )
    assert Decade(1950, official_def=True).time_span == (1951, 1960)


def test_positive_decade_with_take():
    assert Decade(1970).take([1, "half"]).interval == Interval(
        Date(1970, 1, 1), Date(1974, 12, 31)
    )
    assert Decade(1970).take(type="early").interval == Interval(
        Date(1970, 1, 1), Date(1971, 12, 31)
    )
    assert Decade(1970).take(type="late").interval == Interval(
        Date(1978, 1, 1), Date(1979, 12, 31)
    )
    assert Decade(1970).take(type="mid").interval == Interval(
        Date(1974, 1, 1), Date(1975, 12, 31)
    )
    assert Decade(1970).take(3).interval == Interval(
        Date(1972, 1, 1), Date(1972, 12, 31)
    )


def test_negative_decade():
    assert Decade(-1770).interval == Interval(
        neg(Date(0, 12, 31), 1779), neg(YEAR_ZERO, 1770)
    )
    assert Decade(-1770).time_span == (-1779, -1770)

    assert Decade(-1950, official_def=True).interval == Interval(
        neg(Date(0, 12, 31), 1960), neg(YEAR_ZERO, 1951)
    )
    assert Decade(-1950, official_def=True).time_span == (-1960, -1951)


def test_negative_decade_with_take():
    assert Decade(-1970).take([1, "half"]).interval == Interval(
        neg(Date(0, 12, 31), 1974), neg(YEAR_ZERO, 1970)
    )
    assert Decade(-1970).take(type="early").interval == Interval(
        neg(Date(0, 12, 31), 1971), neg(YEAR_ZERO, 1970)
    )
    assert Decade(-1970).take(type="late").interval == Interval(
        neg(Date(0, 12, 31), 1979), neg(YEAR_ZERO, 1978)
    )
    assert Decade(-1970).take(type="mid").interval == Interval(
        neg(Date(0, 12, 31), 1975), neg(YEAR_ZERO, 1974)
    )
    assert Decade(-1970).take(3).interval == Interval(
        neg(YEAR_ZERO, 1972), neg(Date(0, 12, 31), 1972)
    )


def test_invalid_take_with_errors():
    with pytest.raises(ValueError, match="out of range"):
        Decade(1970).take(99)
    with pytest.raises(ValueError, match="not a valid type"):
        Decade(1970).take(type="abc")
    with pytest.raises(ValueError, match="out of range"):
        Decade(1970).take(3, type="half")
    with pytest.raises(ValueError, match="out of range"):
        Decade(1970).take(4, type="third")
    with pytest.raises(ValueError, match="out of range"):
        Decade(1970).take(5, type="quarter")


def test_invalid_take_without_errors():
    full = Interval(Date(1970, 1, 1), Date(1979, 12, 31))
    assert Decade(1970).take(99, ignore_errors=True).interval == full
    assert Decade(1970).take([3, "half"], ignore_errors=True).interval == full
    assert Decade(1970).take([4, "third"], ignore_errors=True).interval == full
    assert Decade(1970).take([5, "quarter"], ignore_errors=True).interval == full
    assert Decade(1970).take(type="abc", ignore_errors=True).interval == full
