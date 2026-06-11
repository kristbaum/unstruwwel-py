"""The text-parsing pipeline that turns standardized tokens into periods."""

from __future__ import annotations

from typing import List, Optional

import regex as re

from .languages import load_languages
from .guess import guess_language
from .periods import Century, Decade, Periods, Year

_TOKEN = re.compile(r"([0-9]+)|(\p{L}+)|(\?)")


# -- token predicates --------------------------------------------------------
def is_year(token) -> bool:
    return str(token).isdigit() and 100 <= int(token) <= 2900


def is_year_addition(token) -> bool:
    return str(token).isdigit() and 1 <= int(token) <= 99


def is_number(token) -> bool:
    return token is not None and str(token).isdigit()


def _at(tokens, pos):
    """1-based indexing that returns ``None`` outside the valid range."""
    if 1 <= pos <= len(tokens):
        return tokens[pos - 1]
    return None


def extract_groups(text: str) -> List[str]:
    """Split standardized text into number / word / ``?`` tokens."""
    return [m.group(0) for m in _TOKEN.finditer(text)]


def _last_window(words) -> list:
    window = list(words)[-5:]
    if len(window) < 5:
        window = [None] * 4 + window
    return window


# -- period builders ---------------------------------------------------------
def build_century(words, negative, uncertain=False):
    and_positions = [i + 1 for i, w in enumerate(words) if w == "and"]
    markers = [0] + [p - 1 for p in and_positions]
    ends = markers[1:] + [len(words)]

    centuries = [
        get_century(words[markers[i]:ends[i]], negative)
        for i in range(len(markers))
    ]
    centuries = [c for c in centuries if c is not None]
    if not centuries:
        return None

    result = Periods(parts=centuries) if len(centuries) > 1 else centuries[0]
    if uncertain:
        result.fuzzy = -1
    return result


def get_century(words, negative, uncertain=False):
    window = _last_window(words)
    if uncertain:
        window = ["?"] + window
    if negative and window[-1] is not None:
        window[-1] = "-" + str(window[-1])

    x_take = [window[-3], window[-2]]
    try:
        period = Century(window[-1]).set_additions(window)
    except (ValueError, TypeError):
        return None  # no usable century value (e.g. an empty sub-segment)
    return period.take(x_take, ignore_errors=True)


def get_decade(words, uncertain=False):
    window = _last_window(words)
    if uncertain:
        window = ["?"] + window

    x_take = [window[-3], window[-2]]
    try:
        period = Decade(window[-1]).set_additions(window)
    except (ValueError, TypeError):
        return None
    return period.take(x_take, ignore_errors=True)


def get_year(words, negative, uncertain=False):
    window = _last_window(words)
    if uncertain:
        window = ["?"] + window

    if is_number(window[-2]):
        x_take = [window[-2], window[-3]]
    else:
        x_take = [window[-3], window[-2]]
    if negative and window[-1] is not None:
        window[-1] = "-" + str(window[-1])

    try:
        period = Year(window[-1]).set_additions(window)
    except (ValueError, TypeError):
        return None  # value out of range (e.g. a typo'd or future year)
    return period.take(x_take, ignore_errors=True)


def _is_digits(token) -> bool:
    return isinstance(token, str) and token.isdigit()


def _is_year_token(token) -> bool:
    """A numeric (optionally negative) year string or an already-built period."""
    if isinstance(token, Periods):
        return True
    if not isinstance(token, str):
        return False
    return token[1:].isdigit() if token.startswith("-") else token.isdigit()


def get_period(words, uncertain=False):
    window = list(words)[-5:]
    if uncertain:
        window = ["?"] + window

    # Complete an abbreviated trailing year, e.g. "1656 57" -> "1656 1657" or
    # "1713 14" -> "1713 1714". Only meaningful when both trailing tokens are
    # plain digit strings; never run string surgery on words or period objects.
    if len(window) > 1 and _is_digits(window[-1]) and _is_digits(window[-2]):
        last, prev = window[-1], window[-2]
        if len(last) < len(prev):
            window[-1] = prev[: len(prev) - len(last)] + last

    # Only digit strings / period objects are valid interval parts; word tokens
    # such as "approximate", "before" or "?" are flags read by set_additions.
    parts = [t for t in window if _is_year_token(t)]
    return Periods(parts=parts).set_additions(window)


# -- the core resolver -------------------------------------------------------
def get_intervals(tokens, start, end):
    n = len(tokens)
    uncertain = _at(tokens, min(end + 1, n)) == "?"

    numbers = [i for i in range(1, end + 1) if is_number(tokens[i - 1])]
    if not numbers:
        return None
    last_number = numbers[-1]
    if start > last_number:
        return None

    y = [t for t in tokens[start - 1:last_number] if t != "?"]
    next_char = min(max(numbers) + 1, n)

    if "century" in tokens[start - 1:end]:
        negative = _at(tokens, max(end + 1, n)) == "bc"
        return build_century(y, negative, uncertain)
    if _at(tokens, next_char) == "s":
        return get_decade(y, uncertain)
    if len(str(y[-1])) < 4:
        return get_period(y, uncertain)

    negative = _at(tokens, max(end + 1, n)) == "ante"
    return get_year(y, negative, uncertain)


def get_dates(tokens, scheme):
    n = len(tokens)
    marks = sorted(
        i for i in range(1, n + 1)
        if tokens[i - 1] == "century" or is_year(tokens[i - 1])
    )

    if not marks:
        return (None, None) if scheme == "time-span" else None

    if len(marks) < n:
        addition_positions = [
            i for i in range(1, n + 1) if is_year_addition(tokens[i - 1])
        ]
        markers = [0] + [
            (m + 1 if (m + 1) in addition_positions else m) for m in marks
        ]
        markers = [m for m in markers if m < n]
        if markers and markers[-1] == 1:
            markers = [markers[0]]

        ends = markers[1:] + [n]
        segments = []
        for i in range(len(markers)):
            segment = get_intervals(tokens, markers[i] + 1, ends[i])
            if segment is not None:
                segments.append(segment)
    else:
        segments = [get_period(tokens)]

    if not segments:
        return (None, None) if scheme == "time-span" else None

    if scheme == "time-span":
        return get_period(segments).time_span
    if scheme == "iso-format":
        return get_period(segments).iso_format
    return segments  # scheme == "object"


def unstruwwel(
    x,
    language: Optional[str] = None,
    scheme: str = "time-span",
    fuzzify=(0, 0),
    verbose: bool = False,
):
    """Detect and parse historic dates.

    Args:
        x: A string or iterable of strings to parse.
        language: ISO 639-1 code (e.g. ``"en"``, ``"de"``). If ``None`` the
            language is detected automatically.
        scheme: One of ``"time-span"`` (a ``(start, end)`` tuple of years),
            ``"iso-format"`` (an ISO 8601:2-2019 string), or ``"object"``
            (a list of :class:`~unstruwwel.periods.Periods`).
        fuzzify: Reserved for compatibility; currently unused.
        verbose: If ``True``, print the detected language.

    Returns:
        The parsed result for a single string input, or a list of results
        aligned with the input sequence.
    """
    scheme = scheme.lower()
    if scheme not in ("iso-format", "time-span", "object"):
        raise ValueError(f"`{scheme}` is not a valid scheme")
    if len(fuzzify) != 2:
        raise ValueError("`fuzzify` must have length 2")

    scalar_input = isinstance(x, str) or x is None
    values = [x] if scalar_input else list(x)
    if not values:
        raise ValueError("`x` must not be empty")
    texts = ["" if v is None else str(v) for v in values]

    languages = load_languages()
    if language is None:
        language = guess_language(texts, verbose=verbose)
    elif isinstance(language, str):
        language = [language]
    else:
        language = list(language)

    invalid = [name for name in language if name not in languages]
    if invalid:
        raise ValueError(
            f"`{invalid[0]}` is either not defined in ISO 639-1 "
            "or not yet implemented."
        )

    # de-duplicate while preserving the mapping back to every input position
    unique = {}
    order = []
    for text in texts:
        if text not in unique:
            unique[text] = _resolve(text, language, languages, scheme)
            order.append(text)

    results = [unique[text] for text in texts]
    return results[0] if scalar_input else results


def _resolve(text, language, languages, scheme):
    standardized = text
    for name in language:
        standardized = languages[name].standardize(standardized)
    tokens = extract_groups(standardized)
    return get_dates(tokens, scheme)
