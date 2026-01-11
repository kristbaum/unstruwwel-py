"""Date parsing logic (day, month, year combinations)."""

from __future__ import annotations
import re
from typing import List, Optional, Tuple

from ..dates import Period, period_for_month, period_for_year, MONTHS
from ..resources import LanguageSpec


def parse_date(
    low: str, txt: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse a plain year.

    Args:
        low: Lowercase input text
        txt: Original (stripped) input text
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    m = re.fullmatch(r"(-?\d{3,4})", txt)
    if m:
        y = int(m.group(1))
        p = period_for_year(y)
        p.fuzzy = fuzzy
        return p
    return None


def parse_month_year(
    low: str, mon_pat_cap: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse month + year expression.

    Args:
        low: Lowercase input text
        mon_pat_cap: Capturing month pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    m = re.fullmatch(rf"{mon_pat_cap}\s+(\d{{3,4}})", low)
    if m:
        y = int(m.group(2))
        tok = m.group(1)
        mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
        if mnum is not None:
            p = period_for_month(y, mnum)
            p.fuzzy = fuzzy
            return p
    return None


def parse_day_month_year(
    low: str, mon_pat_cap: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse exact day Month D, YYYY (English style).

    Args:
        low: Lowercase input text
        mon_pat_cap: Capturing month pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    m = re.fullmatch(rf"{mon_pat_cap}\s+(\d{{1,2}}),\s*(\d{{3,4}})", low)
    if m:
        y = int(m.group(3))
        d = int(m.group(2))
        tok = m.group(1)
        mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
        if mnum is not None:
            p = Period(start=(y, mnum, d), end=(y, mnum, d))
            p.fuzzy = fuzzy
            return p
    return None


def parse_german_date(
    low: str, mon_pat_cap: str, spec: Optional[LanguageSpec], fuzzy: int
) -> List[Tuple[Period, Tuple[int, int]]]:
    """Parse German-style dates: "15. januar 1750".

    Args:
        low: Lowercase input text
        mon_pat_cap: Capturing month pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        List of (Period, (start, end)) tuples for matched spans
    """
    results = []
    for m in re.finditer(rf"(\d{{1,2}})\.\s*{mon_pat_cap}\s+(\d{{3,4}})", low):
        d = int(m.group(1))
        month_tok = m.group(2)
        mm = spec.months.get(month_tok) if spec else MONTHS.get(month_tok)
        if mm is None:
            continue
        y = int(m.group(3))
        p = Period(start=(y, mm, d), end=(y, mm, d))
        p.fuzzy = fuzzy
        results.append((p, (m.start(), m.end())))
    return results
