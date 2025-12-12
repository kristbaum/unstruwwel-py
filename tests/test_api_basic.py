import math

from unstruwwel import unstruwwel


def test_unstruwwel_basic_english_examples_subset():
    dates = [
        "5th century b.c.",
        "unknown",
        "late 16th century",
        "mid-12th century",
        "mid-1880s",
        "June 1963",
        "August 11, 1958",
        "ca. 1920",
        "before 1856",
        "after June 1860",
    ]

    assert unstruwwel(dates, "en", scheme="iso-format") == [
        "-0500-12-31/-0401-01-01",
        None,
        "1586-01-01/1600-12-31",
        "1146-01-01/1155-12-31",
        "1884-01-01/1885-12-31",
        "1963-06-01/1963-06-30",
        "1958-08-11/1958-08-11",
        "1920-01-01~/1920-12-31~",
        "..1855-12-31",
        "1860-07-01..",
    ]

    spans = unstruwwel(dates, "en", scheme="time-span")
    assert spans[0] == (-500.0, -401.0)
    assert spans[1][0] != spans[1][0] and spans[1][1] != spans[1][1]  # nan,nan
    assert spans[2] == (1586.0, 1600.0)
    assert spans[3] == (1146.0, 1155.0)
    assert spans[4] == (1884.0, 1885.0)
    assert spans[5] == (1963.0, 1963.0)
    assert spans[7] == (1920.0, 1920.0)
    assert spans[8] == (-math.inf, 1855.0)
    assert spans[9] == (1860.0, math.inf)


def test_unstruwwel_scalar_input_returns_scalar():
    assert unstruwwel("June 1963", "en", scheme="iso-format") == "1963-06-01/1963-06-30"


def test_unstruwwel_basic_german_examples_subset():
    dates = [
        "undatiert",
        "1460?",
        "wohl nach 1923",
        "spätestens 1750er Jahre",
    ]

    assert unstruwwel(dates, "de", scheme="iso-format") == [
        None,
        "1460-01-01~/1460-12-31~",
        "1924-01-01?..",
        "..1749-12-31",
    ]
