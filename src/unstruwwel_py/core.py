"""Core parsing functionality for historical date strings."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple, Union

from .dates import Period
from .resources import get_language_spec
from .lang import guess_language
from .parsers import (
    parse_century,
    parse_decade,
    parse_date,
    parse_month_year,
    parse_day_month_year,
    parse_before_after,
    parse_year_interval,
    parse_season,
)
from .parsers.intervals import parse_multi_dates


@dataclass
class Parsed:
    text: str
    time_span: Tuple[Optional[float], Optional[float]]
    iso_format: Optional[str]
    fuzzy: int = 0  # -1 = approximate, 0 = exact, 1 = uncertain


Result = Union[Parsed, Tuple[Optional[float], Optional[float]]]


def get_item(x: Sequence[Any], i: int = 1) -> Any:
    """R-like helper to fetch the i-th item (1-based)."""
    return x[i - 1]


def _emit(p: Period, scheme: str) -> Result:
    """Convert a Period to the requested output format."""
    if scheme == "time-span":
        return (p.time_span[0], p.time_span[1])
    if scheme == "iso-format":
        return p.iso_format  # type: ignore[return-value]
    # object
    return Parsed(
        text="", time_span=p.time_span, iso_format=p.iso_format, fuzzy=p.fuzzy
    )


def unstruwwel(
    texts: Optional[Union[str, Sequence[Optional[str]]]],
    language: Optional[str] = None,
    scheme: str = "time-span",
) -> List[Result]:
    """Parse historic dates (subset) into time spans, iso-format, or objects.

    Supported:
    - unknown/undatiert -> NA
    - plain year (incl. negatives) -> full-year span
    - month name + year -> month span
    - seasons + year -> season span
    - before/after + (month?) year -> open-ended intervals
    - year interval like 1752/60 -> 1752..1760
    - decade forms: '1840s' (en), '1760er Jahre' (de)
    - centuries: '19. Jh.' (de), '5. Jh. v. Chr', 'last third 17th cent' (en)
    - fuzzy: '~' approximate, '?' uncertain terms
    """
    if texts is None or isinstance(texts, str):
        texts = [texts]

    # Validate language per tests: require language for object scheme
    if language is None and scheme == "object":
        raise ValueError("language is required for scheme=object")
    if language is not None and language not in {"en", "de", "fr"}:
        raise ValueError("invalid language code")

    out: List[Result] = []
    for t in texts:
        result = _parse_single(t, language, scheme)
        if isinstance(result, list):
            out.extend(result)
        else:
            out.append(result)
    return out


def _parse_single(
    t: Optional[str], language: Optional[str], scheme: str
) -> Union[Result, List[Result]]:
    """Parse a single text input."""
    # Handle unknown/null
    if t is None or (
        isinstance(t, str) and t.strip().lower() in {"undatiert", "unknown"}
    ):
        if scheme == "object":
            return Parsed(
                text=t or "", time_span=(None, None), iso_format=None, fuzzy=0
            )
        return (None, None)

    txt = t.strip()
    lang = language
    if lang is None:
        try:
            gl = guess_language([txt], verbose=False)
            lang = gl if isinstance(gl, str) else gl[0]
        except Exception:
            lang = "en"

    low = txt.lower()
    spec = get_language_spec(lang) if lang else None
    fuzzy = _compute_fuzzy(low, spec)

    # Build patterns
    mon_pat_base = (
        spec.month_pattern()
        if spec
        else r"(?:january|february|march|april|may|june|july|august|september|october|november|december)"
    )
    mon_pat_cap = f"({mon_pat_base})"
    sp_base = spec.season_pattern() if spec else r"(?:spring|summer|autumn|winter)"
    sp_cap = f"({sp_base})"
    before_pat = spec.before_pattern() if spec else r"(?:before)"
    after_pat = spec.after_pattern() if spec else r"(?:after)"
    season_pat = spec.season_pattern() if spec else r"(?:spring|summer|autumn|winter)"

    # Try multi-date parsing first
    multi_results = parse_multi_dates(
        low, mon_pat_base, mon_pat_cap, before_pat, after_pat, season_pat, spec, fuzzy
    )
    if multi_results:
        return [_emit(p, scheme) for p, _ in multi_results]

    # Try each parser in order
    parsers = [
        lambda: parse_decade(low, txt, spec, fuzzy),
        lambda: parse_year_interval(txt, fuzzy),
        lambda: parse_before_after(low, mon_pat_cap, season_pat, spec, fuzzy),
        lambda: parse_season(low, sp_cap, spec, fuzzy),
        lambda: parse_month_year(low, mon_pat_cap, spec, fuzzy),
        lambda: parse_day_month_year(low, mon_pat_cap, spec, fuzzy),
        lambda: parse_century(low, spec, fuzzy),
        lambda: parse_date(low, txt, spec, fuzzy),
    ]

    for parser in parsers:
        result = parser()
        if result is not None:
            return _emit(result, scheme)

    # Fallback
    if scheme == "object":
        return Parsed(
            text=t or "", time_span=(None, None), iso_format=None, fuzzy=fuzzy
        )
    return (None, None)


def _compute_fuzzy(low: str, spec) -> int:
    """Compute fuzzy marker from text."""
    fuzzy = 0
    if spec and any(k in low for k in spec.approximate):
        fuzzy = -1
    elif any(k in low for k in ["circa", "ca", "ca."]):
        fuzzy = -1
    if spec and any(k in low for k in spec.uncertain):
        fuzzy = 1
    elif any(k in low for k in ["uncertain", "perhaps", "probably"]):
        fuzzy = 1
    return fuzzy
