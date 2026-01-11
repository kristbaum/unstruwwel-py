import pytest

from unstruwwel_py.periods import Year


def test_invalid_year():
    with pytest.raises(Exception):
        Year(197.5)  # type: ignore[arg-type]
    with pytest.raises(Exception):
        Year([197, 198])  # type: ignore[arg-type]


def test_invalid_take_with_year():
    with pytest.raises(Exception):
        Year(1900).take(type="j")


def test_positive_year():
    y = Year(1750)
    assert y.time_span == (1750, 1750)


def test_positive_year_with_month():
    y = Year(1750)
    y.take(type="may")
    assert y.time_span == (1750, 1750)


def test_positive_year_with_month_and_day():
    y = Year(1750)
    y.take(5, "april")
    assert y.time_span == (1750, 1750)


def test_negative_year():
    y = Year(-1750)
    assert y.time_span == (-1750, -1750)


def test_negative_year_with_month():
    y = Year(-1750)
    y.take(type="may")
    assert y.time_span == (-1750, -1750)


def test_negative_year_with_month_and_day():
    y = Year(-1750)
    y.take(5, "april")
    assert y.time_span == (-1750, -1750)
