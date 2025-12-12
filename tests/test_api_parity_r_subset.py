import math
import pytest

from unstruwwel import unstruwwel


@pytest.mark.parametrize(
    "text,lang,expected",
    [
        ("1752/60", "en", "1752-01-01/1760-12-31"),
        ("Autumn 1945", "en", "1945-09-01/1945-11-30"),
        ("vor dem Sommer 1907", "de", "..1907-05-31"),
        ("May 1901", "en", "1901-05-01/1901-05-31"),
        ("January 1, 1856", "en", "1856-01-01/1856-01-01"),
        ("1840s", "en", "1840-01-01/1849-12-31"),
        ("1760er Jahre", "de", "1760-01-01/1769-12-31"),
        ("etwa 1550er Jahre", "de", "1550-01-01?/1559-12-31?"),
        ("1st half 5th century", "en", "0401-01-01/0450-12-31"),
        ("19. Jh.", "de", "1801-01-01/1900-12-31"),
        ("5. Jh. v. Chr", "de", "-0500-12-31/-0401-01-01"),
        ("last third 17th cent", "en", "1667-01-01/1700-12-31"),
        ("circa 18th century", "en", "1701-01-01~/1800-12-31~"),
        ("ca. 1. Hälfte 2. Jh.", "de", "0101-01-01~/0150-12-31~"),
        ("ca. 2. Jh. v. Chr", "de", "-0200-12-31~/-0101-01-01~"),
    ],
)
def test_iso_format_parity_subset(text, lang, expected):
    assert unstruwwel(text, lang, scheme="iso-format") == expected


def test_multiple_dates_in_one_string_parity():
    # From R tests: "(Guss vor 1906) 1897" yields 2 results.
    out = unstruwwel("(Guss vor 1906) 1897", "de", scheme="iso-format")
    assert out == ["..1905-12-31", "1897-01-01/1897-12-31"]


def test_multiple_days_range_parity():
    out = unstruwwel("13. Juli 1882 - 15. Juli 1882", "de", scheme="iso-format")
    assert out == ["1882-07-13/1882-07-13", "1882-07-15/1882-07-15"]


def test_language_required_when_none():
    # Numeric-only can't be guessed reliably.
    with pytest.raises(Exception):
        unstruwwel("1460", None, scheme="iso-format")


def test_guess_language_smoke():
    assert unstruwwel("undatiert", None, scheme="iso-format") is None


def test_invalid_language_errors():
    with pytest.raises(Exception):
        unstruwwel("1460", "bo", scheme="iso-format")
