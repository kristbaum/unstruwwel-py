import pytest

from unstruwwel_py.periods import Decade


def test_invalid_decade():
    with pytest.raises(Exception):
        Decade(203)
    with pytest.raises(Exception):
        Decade(2021)
    with pytest.raises(Exception):
        Decade(197.5)  # type: ignore[arg-type]
    with pytest.raises(Exception):
        Decade([197, 198])  # type: ignore[arg-type]


def test_positive_decade():
    d = Decade(1770)
    assert d.time_span == (1770, 1779)
    d = Decade(1950)
    assert d.time_span == (1950, 1959)


def test_positive_decade_with_take():
    d = Decade(1970)
    assert d.take(1, type="half")
    assert d.take(type="early")
    assert d.take(type="late")
    assert d.take(type="mid")
    assert d.take(3)


def test_negative_decade():
    d = Decade(-1770)
    assert d.time_span == (-1779, -1770)
    d = Decade(-1950)
    assert d.time_span == (-1959, -1950)


def test_negative_decade_with_take():
    d = Decade(-1970)
    assert d.take(1, type="half")
    assert d.take(type="early")
    assert d.take(type="late")
    assert d.take(type="mid")
    assert d.take(3)


def test_invalid_take_with_errors():
    d = Decade(1970)
    with pytest.raises(Exception):
        d.take(99)
    with pytest.raises(Exception):
        d.take(type="abc")
    with pytest.raises(Exception):
        d.take(3, type="half")
    with pytest.raises(Exception):
        d.take(4, type="third")
    with pytest.raises(Exception):
        d.take(5, type="quarter")


def test_invalid_take_without_errors():
    d = Decade(1970)
    assert d.take(99, ignore_errors=True)
    assert d.take(3, "half", ignore_errors=True)
    assert d.take(4, "third", ignore_errors=True)
    assert d.take(5, "quarter", ignore_errors=True)
    assert d.take(type="abc", ignore_errors=True)
