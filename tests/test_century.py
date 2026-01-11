import pytest

from unstruwwel_py.periods import Century


def test_invalid_century():
    with pytest.raises(Exception):
        Century(22)
    with pytest.raises(Exception):
        Century("20.22")
    with pytest.raises(Exception):
        Century([10, 20])  # type: ignore[arg-type]


def test_positive_century():
    c = Century("1")
    assert c.time_span == (1, 100)
    c = Century(15)
    assert c.time_span == (1401, 1500)


def test_positive_century_with_take():
    c = Century(15)
    assert isinstance(c.take((1, "half")), Century)
    assert isinstance(c.take(1, type="half"), Century)
    assert isinstance(c.take(2, type="quarter"), Century)
    assert isinstance(c.take("last", type="third"), Century)
    assert isinstance(c.take(type="early"), Century)
    assert isinstance(c.take(type="late"), Century)
    assert isinstance(c.take(type="mid"), Century)
    assert isinstance(c.take(3), Century)
    assert isinstance(c.take("last", "half"), Century)


def test_negative_century():
    c = Century("-1")
    assert c.time_span == (-100, -1)
    c = Century(-15)
    assert c.time_span == (-1500, -1401)


def test_negative_century_with_take():
    c = Century(-15)
    assert isinstance(c.take((1, "half")), Century)
    assert isinstance(c.take(1, type="half"), Century)
    assert isinstance(c.take(2, type="quarter"), Century)
    assert isinstance(c.take("last", type="third"), Century)
    assert isinstance(c.take(type="early"), Century)
    assert isinstance(c.take(type="late"), Century)
    assert isinstance(c.take(type="mid"), Century)
    assert isinstance(c.take(3), Century)


def test_invalid_take_with_errors():
    c = Century(15)
    with pytest.raises(Exception):
        c.take(999)
    with pytest.raises(Exception):
        c.take(type="abc")
    with pytest.raises(Exception):
        c.take(3, type="half")
    with pytest.raises(Exception):
        c.take(4, type="third")
    with pytest.raises(Exception):
        c.take(5, type="quarter")


def test_invalid_take_without_errors():
    c = Century(15)
    assert isinstance(c.take(999, ignore_errors=True), Century)
    assert isinstance(c.take(3, "half", ignore_errors=True), Century)
    assert isinstance(c.take(4, "third", ignore_errors=True), Century)
    assert isinstance(c.take(5, "quarter", ignore_errors=True), Century)
    assert isinstance(c.take(type="abc", ignore_errors=True), Century)
