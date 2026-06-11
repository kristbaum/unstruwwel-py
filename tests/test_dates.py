"""Unit tests for the proleptic-Gregorian date arithmetic."""

import datetime

import pytest

from unstruwwel.dates import Date, Interval


@pytest.mark.parametrize(
    "year, month, day",
    [
        (1970, 1, 1),
        (2000, 2, 29),
        (1, 1, 1),
        (1500, 12, 31),
        (2024, 6, 11),
    ],
)
def test_ordinal_roundtrips_against_stdlib(year, month, day):
    d = Date(year, month, day)
    assert d.ordinal == datetime.date(year, month, day).toordinal() - 719163
    assert Date.from_ordinal(d.ordinal) == d


def test_year_zero_is_a_leap_year():
    # Feb 29 of year 0 must round-trip cleanly in the proleptic calendar
    assert Date.from_ordinal(Date(0, 2, 29).ordinal) == Date(0, 2, 29)


def test_negative_years_round_trip():
    for d in [Date(-500, 12, 31), Date(-1, 1, 1), Date(-1750, 6, 15)]:
        assert Date.from_ordinal(d.ordinal) == d


def test_plus_years_crossing_zero():
    assert Date(0, 1, 1).plus_years(-1) == Date(-1, 1, 1)
    assert Date(-1, 1, 1).plus_days(-1) == Date(-2, 12, 31)


def test_plus_months_wraps_year():
    assert Date(1750, 1, 1).plus_months(14) == Date(1751, 3, 1)
    assert Date(1750, 12, 1).plus_months(1) == Date(1751, 1, 1)


def test_plus_days_handles_month_end():
    assert Date(1751, 1, 1).plus_days(-1) == Date(1750, 12, 31)


def test_leap_day_clamps_on_year_shift():
    assert Date(2000, 2, 29).plus_years(1) == Date(2001, 2, 28)


def test_iso_padding():
    assert Date(401, 1, 1).iso() == "0401-01-01"
    assert Date(-500, 12, 31).iso() == "-0500-12-31"
    assert Date(1842, 6, 1).iso() == "1842-06-01"


def test_interval_standardize_orders_endpoints():
    iv = Interval(Date(1900, 1, 1), Date(1800, 1, 1)).standardize()
    assert iv.start == Date(1800, 1, 1)
    assert iv.end == Date(1900, 1, 1)
