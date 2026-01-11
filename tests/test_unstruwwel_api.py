import math
import pytest

from unstruwwel_py import unstruwwel, get_item


def test_no_language_error():
    with pytest.raises(Exception):
        unstruwwel("1460", scheme="object")


def test_invalid_language():
    with pytest.raises(Exception):
        unstruwwel("1460", "bo", scheme="object")


def test_no_date_cases():
    assert get_item(unstruwwel("undatiert", "de")) == (None, None)
    assert get_item(unstruwwel(None, "de")) == (None, None)


def test_date_with_year_simple():
    assert get_item(unstruwwel("1842", "en")) == (1842, 1842)


def test_date_with_year():
    assert get_item(unstruwwel("1842", "en")) == (1842, 1842)


def test_date_with_multiple_years():
    x = unstruwwel("(Guss vor 1906) 1897", "de", scheme="object")
    assert get_item(x, 1).time_span == (-math.inf, 1905)
    assert get_item(x, 2).time_span == (1897, 1897)
    assert get_item(x, 1).iso_format == "..1905-12-31"
    assert get_item(x, 2).iso_format == "1897-01-01/1897-12-31"


def test_year_interval_short():
    assert get_item(unstruwwel("1752/60", "en")) == (1752, 1760)


def test_year_month_and_season_iso():
    x = unstruwwel("Autumn 1945", "en", scheme="object")
    it = get_item(x)
    assert it.time_span == (1945, 1945)
    assert it.iso_format == "1945-09-01/1945-11-30"
    x = unstruwwel("vor dem Sommer 1907", "de", scheme="object")
    it = get_item(x)
    assert it.time_span == (-math.inf, 1907)
    assert it.iso_format.startswith("..1907-")


def test_year_month_iso():
    x = unstruwwel("May 1901", "en", scheme="object")
    it = get_item(x)
    assert it.time_span == (1901, 1901)
    assert it.iso_format == "1901-05-01/1901-05-31"
    x = unstruwwel("after June 1860", "en", scheme="object")
    it = get_item(x)
    assert it.time_span == (1860, math.inf)
    assert it.iso_format.startswith("1860-07-01..")


def test_day_precise_iso():
    x = unstruwwel("January 1, 1856", "en", scheme="object")
    it = get_item(x)
    assert it.time_span == (1856, 1856)
    assert it.iso_format == "1856-01-01/1856-01-01"


def test_date_with_multiple_years_months_days():
    x = unstruwwel("13. Juli 1882 - 15. Juli 1882", "de", scheme="object")
    assert get_item(x, 1).time_span == (1882, 1882)
    assert get_item(x, 2).time_span == (1882, 1882)
    assert get_item(x, 1).iso_format == "1882-07-13/1882-07-13"
    assert get_item(x, 2).iso_format == "1882-07-15/1882-07-15"


def test_decade_basic():
    assert get_item(unstruwwel("1840s", "en")) == (1840, 1849)
    assert get_item(unstruwwel("1760er Jahre", "de")) == (1760, 1769)


def test_date_with_uncertain_decade():
    x = unstruwwel("etwa 1550er Jahre", "de", scheme="object")
    assert get_item(x).fuzzy == 1
    assert get_item(x).time_span == (1550, 1559)
    assert get_item(x).iso_format == "1550-01-01?/1559-12-31?"


def test_century_basic():
    x = get_item(unstruwwel("19. Jh.", "de"))
    assert x == (1801, 1900)
    x = get_item(unstruwwel("5. Jh. v. Chr", "de"))
    assert x == (-500, -401)
    # english phrase
    x = get_item(unstruwwel("last third 17th cent", "en"))
    assert x == (1667, 1700)


def test_date_with_uncertain_century():
    x = unstruwwel("circa 18th century", "en", scheme="object")
    assert get_item(x).fuzzy == -1
    assert get_item(x).time_span == (1701, 1800)
    assert get_item(x).iso_format == "1701-01-01~/1800-12-31~"


def test_trailing_zero():
    x = unstruwwel("ca. 1. Hälfte 2. Jh.", "de", scheme="object")
    assert get_item(x).time_span == (101, 150)
    assert get_item(x).iso_format == "0101-01-01~/0150-12-31~"
    x = unstruwwel("ca. 2. Jh. v. Chr", "de", scheme="object")
    assert get_item(x).time_span == (-200, -101)
    assert get_item(x).iso_format == "-0200-12-31~/-0101-01-01~"


def test_duplicate_dates():
    x = unstruwwel(["late 16th century", "ca. 1920"] * 10, "en")
    assert x[0] == x[2]
    assert x[1] == x[3]
