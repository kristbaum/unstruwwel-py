"""unstruwwel: detect and parse historic dates, e.g. to ISO 8601:2-2019."""

from __future__ import annotations

from .core import unstruwwel
from .dates import Date, Interval
from .guess import guess_language, guess_midas
from .languages import load_languages
from .periods import Century, Decade, Periods, Year

__all__ = [
    "unstruwwel",
    "guess_language",
    "guess_midas",
    "load_languages",
    "Periods",
    "Century",
    "Decade",
    "Year",
    "Date",
    "Interval",
]

__version__ = "0.1.0"
