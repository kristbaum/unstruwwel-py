import math

import pytest

from unstruwwel import unstruwwel


def test_no_language():
    # "1460" has no letters, so the language cannot be detected
    with pytest.raises(Exception):
        unstruwwel("1460", scheme="object")


def test_invalid_language():
    with pytest.raises(Exception):
        unstruwwel("1460", "bo", scheme="object")


def test_no_date():
    assert unstruwwel("undatiert", "de") == (None, None)
    assert unstruwwel(None, "de") == (None, None)


def test_approximate_date():
    x = unstruwwel("1460?", "en", scheme="object")[0]
    assert x.fuzzy == -1
    assert x.time_span == (1460, 1460)
    assert x.iso_format == "1460-01-01~/1460-12-31~"


def test_uncertain_date():
    x = unstruwwel("etwa 1842", "de", scheme="object")[0]
    assert x.fuzzy == 1
    assert x.time_span == (1842, 1842)
    assert x.iso_format == "1842-01-01?/1842-12-31?"


def test_date_with_year():
    assert unstruwwel("1842", "en") == (1842, 1842)


def test_date_with_multiple_years():
    x = unstruwwel("(Guss vor 1906) 1897", "de", scheme="object")
    assert x[0].time_span == (-math.inf, 1905)
    assert x[1].time_span == (1897, 1897)
    assert x[0].iso_format == "..1905-12-31"
    assert x[1].iso_format == "1897-01-01/1897-12-31"


def test_date_with_year_interval():
    assert unstruwwel("1752/60", "en") == (1752, 1760)


def test_date_with_year_and_season():
    x = unstruwwel("Autumn 1945", "en", scheme="object")[0]
    assert x.time_span == (1945, 1945)
    assert x.iso_format == "1945-09-01/1945-11-30"

    x = unstruwwel("vor dem Sommer 1907", "de", scheme="object")[0]
    assert x.time_span == (-math.inf, 1907)
    assert x.iso_format == "..1907-05-31"


def test_date_with_year_and_month():
    x = unstruwwel("May 1901", "en", scheme="object")[0]
    assert x.time_span == (1901, 1901)
    assert x.iso_format == "1901-05-01/1901-05-31"

    x = unstruwwel("after June 1860", "en", scheme="object")[0]
    assert x.time_span == (1860, math.inf)
    assert x.iso_format == "1860-07-01.."


def test_date_with_year_month_and_day():
    x = unstruwwel("January 1, 1856", "en", scheme="object")[0]
    assert x.time_span == (1856, 1856)
    assert x.iso_format == "1856-01-01/1856-01-01"


def test_date_with_multiple_years_months_and_days():
    x = unstruwwel("13. Juli 1882 - 15. Juli 1882", "de", scheme="object")
    assert x[0].time_span == (1882, 1882)
    assert x[1].time_span == (1882, 1882)
    assert x[0].iso_format == "1882-07-13/1882-07-13"
    assert x[1].iso_format == "1882-07-15/1882-07-15"


def test_date_with_decade():
    assert unstruwwel("1840s", "en") == (1840, 1849)
    assert unstruwwel("1760er Jahre", "de") == (1760, 1769)


def test_date_with_uncertain_decade():
    x = unstruwwel("etwa 1550er Jahre", "de", scheme="object")[0]
    assert x.fuzzy == 1
    assert x.time_span == (1550, 1559)
    assert x.iso_format == "1550-01-01?/1559-12-31?"


def test_date_with_century():
    x = unstruwwel("1st half 5th century", "en", scheme="object")[0]
    assert x.time_span == (401, 450)
    assert x.iso_format == "0401-01-01/0450-12-31"

    assert unstruwwel("19. Jh.", "de") == (1801, 1900)
    assert unstruwwel("5. Jh. v. Chr", "de") == (-500, -401)
    assert unstruwwel("last third 17th cent", "en") == (1667, 1700)


def test_date_with_uncertain_century():
    x = unstruwwel("circa 18th century", "en", scheme="object")[0]
    assert x.fuzzy == -1
    assert x.time_span == (1701, 1800)
    assert x.iso_format == "1701-01-01~/1800-12-31~"


def test_trailing_zero():
    x = unstruwwel("ca. 1. Hälfte 2. Jh.", "de", scheme="object")[0]
    assert x.time_span == (101, 150)
    assert x.iso_format == "0101-01-01~/0150-12-31~"

    x = unstruwwel("ca. 2. Jh. v. Chr", "de", scheme="object")[0]
    assert x.time_span == (-200, -101)
    assert x.iso_format == "-0200-12-31~/-0101-01-01~"


def test_combined_centuries():
    assert unstruwwel(
        "letztes Drittel 15. und 1. Hälfte 16. Jahrhundert", "de"
    ) == (1467, 1550)


def test_duplicate_dates():
    x = unstruwwel(["late 16th century", "ca. 1920"] * 10, "en")
    assert x[0] == x[2]
    assert x[1] == x[3]


def test_midas_date_with_negative_year():
    assert unstruwwel("2100ante/1550ante", "de") == (-2100, -1550)


def test_invalid_scheme():
    with pytest.raises(ValueError):
        unstruwwel("1842", "en", scheme="nonsense")


def test_list_input_returns_list():
    result = unstruwwel(["1842", "1900"], "en")
    assert result == [(1842, 1842), (1900, 1900)]
