import math

from unstruwwel.core import HistoricalDate, Period, month_period, year_period


def test_iso_exact_interval():
    p = Period(HistoricalDate(1958, 8, 11), HistoricalDate(1958, 8, 11))
    assert p.iso_format() == "1958-08-11/1958-08-11"


def test_iso_open_start_end():
    p1 = Period(None, HistoricalDate(1855, 12, 31))
    assert p1.iso_format() == "..1855-12-31"

    p2 = Period(HistoricalDate(1860, 7, 1), None)
    assert p2.iso_format() == "1860-07-01.."


def test_iso_fuzzy_markers():
    p = year_period(1460, fuzzy=-1)
    assert p.iso_format() == "1460-01-01~/1460-12-31~"

    p2 = year_period(1842, fuzzy=+1)
    assert p2.iso_format() == "1842-01-01?/1842-12-31?"


def test_iso_negative_year_padding():
    p = Period(HistoricalDate(-500, 12, 31), HistoricalDate(-401, 1, 1))
    assert p.iso_format() == "-0500-12-31/-0401-01-01"


def test_time_span_open_ends_and_none():
    p = Period(None, HistoricalDate(1855, 12, 31))
    assert p.time_span() == (-math.inf, 1855.0)

    p2 = Period(HistoricalDate(1860, 7, 1), None)
    assert p2.time_span() == (1860.0, math.inf)

    p3 = Period(None, None)
    a, b = p3.time_span()
    assert math.isnan(a) and math.isnan(b)


def test_month_period_end_of_month():
    p = month_period(1963, 6)
    assert p.iso_format() == "1963-06-01/1963-06-30"
