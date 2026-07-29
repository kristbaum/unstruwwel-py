import pytest

from unstruwwel import Century
from unstruwwel.dates import Date, Interval
from unstruwwel.periods import YEAR_ZERO


def neg(date, years):
    return date.plus_years(-years)


def test_invalid_century():
    with pytest.raises(ValueError, match="not a valid century"):
        Century(22)
    with pytest.raises(ValueError, match="not an integer"):
        Century(20.22)
    with pytest.raises(TypeError, match="not a scalar integer"):
        Century([10, 20])


def test_positive_century():
    assert Century("1").interval == Interval(Date(1, 1, 1), Date(100, 12, 31))
    assert Century("1").time_span == (1, 100)

    assert Century(15).interval == Interval(Date(1401, 1, 1), Date(1500, 12, 31))
    assert Century(15).time_span == (1401, 1500)


def test_positive_century_with_take():
    assert Century(15).take([1, "half"]).interval == Interval(
        Date(1401, 1, 1), Date(1450, 12, 31)
    )
    assert Century(15).take(1, type="half").interval == Interval(
        Date(1401, 1, 1), Date(1450, 12, 31)
    )
    assert Century(15).take(2, type="quarter").interval == Interval(
        Date(1426, 1, 1), Date(1450, 12, 31)
    )
    assert Century(15).take("last", type="third").interval == Interval(
        Date(1467, 1, 1), Date(1500, 12, 31)
    )
    assert Century(15).take(type="early").interval == Interval(
        Date(1401, 1, 1), Date(1415, 12, 31)
    )
    assert Century(15).take(type="late").interval == Interval(
        Date(1486, 1, 1), Date(1500, 12, 31)
    )
    assert Century(15).take(type="mid").interval == Interval(
        Date(1446, 1, 1), Date(1455, 12, 31)
    )
    assert Century(15).take(3).interval == Interval(
        Date(1421, 1, 1), Date(1430, 12, 31)
    )
    assert Century(15).take("last", "half").interval == Interval(
        Date(1451, 1, 1), Date(1500, 12, 31)
    )


def test_negative_century():
    assert Century("-1").interval == Interval(
        neg(Date(0, 12, 31), 100), neg(YEAR_ZERO, 1)
    )
    assert Century("-1").time_span == (-100, -1)

    assert Century(-15).interval == Interval(
        neg(Date(0, 12, 31), 1500), neg(YEAR_ZERO, 1401)
    )
    assert Century(-15).time_span == (-1500, -1401)


def test_negative_century_with_take():
    assert Century(-15).take([1, "half"]).interval == Interval(
        neg(Date(0, 12, 31), 1450), neg(YEAR_ZERO, 1401)
    )
    assert Century(-15).take(2, type="quarter").interval == Interval(
        neg(Date(0, 12, 31), 1450), neg(YEAR_ZERO, 1426)
    )
    assert Century(-15).take("last", type="third").interval == Interval(
        neg(Date(0, 12, 31), 1500), neg(YEAR_ZERO, 1467)
    )
    assert Century(-15).take(type="early").interval == Interval(
        neg(Date(0, 12, 31), 1415), neg(YEAR_ZERO, 1401)
    )
    assert Century(-15).take(type="late").interval == Interval(
        neg(Date(0, 12, 31), 1500), neg(YEAR_ZERO, 1486)
    )
    assert Century(-15).take(type="mid").interval == Interval(
        neg(Date(0, 12, 31), 1455), neg(YEAR_ZERO, 1446)
    )
    assert Century(-15).take(3).interval == Interval(
        neg(Date(0, 12, 31), 1430), neg(YEAR_ZERO, 1421)
    )


def test_invalid_take_with_errors():
    with pytest.raises(ValueError, match="out of range"):
        Century(15).take(999)
    with pytest.raises(ValueError, match="not a valid type"):
        Century(15).take(type="abc")
    with pytest.raises(ValueError, match="out of range"):
        Century(15).take(3, type="half")
    with pytest.raises(ValueError, match="out of range"):
        Century(15).take(4, type="third")
    with pytest.raises(ValueError, match="out of range"):
        Century(15).take(5, type="quarter")


def test_invalid_take_without_errors():
    full = Interval(Date(1401, 1, 1), Date(1500, 12, 31))
    assert Century(15).take(999, ignore_errors=True).interval == full
    assert Century(15).take([3, "half"], ignore_errors=True).interval == full
    assert Century(15).take([4, "third"], ignore_errors=True).interval == full
    assert Century(15).take([5, "quarter"], ignore_errors=True).interval == full
    assert Century(15).take(type="abc", ignore_errors=True).interval == full
