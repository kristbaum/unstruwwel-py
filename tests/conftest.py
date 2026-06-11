import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    path = FIXTURES / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def german_dates():
    return _load("de")


@pytest.fixture(scope="session")
def french_dates():
    return _load("fr")


@pytest.fixture(scope="session")
def english_dates():
    # The English real-world fixture could not be extracted from the R data,
    # so use a representative hand-written sample instead.
    return [
        "5th century b.c.",
        "late 16th century",
        "mid-12th century",
        "mid-1880s",
        "June 1963",
        "August 11, 1958",
        "ca. 1920",
        "before 1856",
        "first half of the 19th century",
        "circa 1901",
        "between 1901 and 1905",
        "the year 1750",
        "spring 1648",
        "end of the 17th century",
        "last third 17th cent",
        "about 1500",
    ]
