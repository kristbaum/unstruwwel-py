"""Interval and before/after parsing logic."""

from __future__ import annotations
import re
from typing import List, Optional, Set, Tuple

from ..dates import Period, period_for_year, MONTHS, MONTH_DAYS
from ..resources import LanguageSpec


def parse_year_interval(txt: str, fuzzy: int) -> Optional[Period]:
    """Try to parse year interval like 1752/60.

    Args:
        txt: Original (stripped) input text
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    m = re.fullmatch(r"(\d{3,4})\/(\d{1,4})", txt)
    if m:
        y1 = int(m.group(1))
        tail = m.group(2)
        if len(tail) < len(m.group(1)):
            y2 = int(str(y1)[: len(m.group(1)) - len(tail)] + tail)
        else:
            y2 = int(tail)
        p = Period(start=(y1, 1, 1), end=(y2, 12, 31))
        p.fuzzy = fuzzy
        return p
    return None


def parse_before_after(
    low: str,
    mon_pat_cap: str,
    season_pat: str,
    spec: Optional[LanguageSpec],
    fuzzy: int,
) -> Optional[Period]:
    """Try to parse before/after expressions.

    Handles:
    - "before 1856"
    - "after June 1860"
    - "vor dem Sommer 1750"

    Args:
        low: Lowercase input text
        mon_pat_cap: Capturing month pattern regex
        season_pat: Season pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    # Check if text starts with a before/after keyword
    before_keywords: Set[str] = spec.before if spec else {"before"}
    after_keywords: Set[str] = spec.after if spec else {"after"}

    expr = 0
    for kw in before_keywords:
        if low.startswith(kw):
            expr = -1
            break
    if expr == 0:
        for kw in after_keywords:
            if low.startswith(kw):
                expr = 1
                break

    if expr == 0:
        return None

    ym = re.findall(mon_pat_cap, low)
    m_season = re.search(rf"({season_pat})", low) if spec else None
    season_tok = m_season.group(1) if m_season else None
    season_name = spec.seasons.get(season_tok) if spec and season_tok else None
    yx = re.findall(r"(-?\d{3,4})", low)

    if not yx:
        return None

    y = int(yx[-1])

    if season_name:
        start_m = (
            3
            if season_name == "spring"
            else 6
            if season_name == "summer"
            else 9
            if season_name == "autumn"
            else 12
        )
        if expr < 0:
            if start_m == 12:
                end_y, end_m, end_d = (y - 1, 11, 30)
            else:
                end_m = start_m - 1
                end_y = y
                end_d = MONTH_DAYS[end_m]
            p = Period(start=(y, 1, 1), end=(end_y, end_m, end_d))
            p.express = -1
        else:
            end_m = start_m + 2
            if start_m == 12:
                start_y, start_mn, start_d = (y + 1, 3, 1)
            elif end_m >= 12:
                start_y, start_mn, start_d = (y + 1, 1, 1)
            else:
                start_y, start_mn, start_d = (y, end_m + 1, 1)
            p = Period(start=(start_y, start_mn, start_d), end=(y, 12, 31))
            p.express = 1
        p.fuzzy = fuzzy
        return p

    if ym:
        mname = ym[-1]
        mnum = spec.months.get(mname) if spec else MONTHS.get(mname)
        if mnum:
            if expr < 0:
                if mnum == 1:
                    end_y, end_m, end_d = (y - 1, 12, 31)
                else:
                    end_y, end_m, end_d = (y, mnum - 1, MONTH_DAYS[mnum - 1])
                p = Period(start=(y, 1, 1), end=(end_y, end_m, end_d))
                p.express = -1
            else:
                start_mn = mnum + 1 if mnum < 12 else 12
                p = Period(start=(y, start_mn, 1), end=(y, 12, 31))
                p.express = 1
            p.fuzzy = fuzzy
            return p

    # Plain year before/after
    if expr < 0:
        p = Period(start=(y, 1, 1), end=(y - 1, 12, 31))
        p.express = -1
    else:
        p = Period(start=(y + 1, 1, 1), end=(y, 12, 31))
        p.express = 1
    p.fuzzy = fuzzy
    return p


def parse_multi_dates(
    low: str,
    mon_pat_base: str,
    mon_pat_cap: str,
    before_pat: str,
    after_pat: str,
    season_pat: str,
    spec: Optional[LanguageSpec],
    fuzzy: int,
) -> Optional[List[Tuple[Period, Tuple[int, int]]]]:
    """Parse multiple date expressions from complex input.

    Used when input contains parentheses, dashes, or multiple dates.

    Args:
        low: Lowercase input text
        mon_pat_base: Non-capturing month pattern regex
        mon_pat_cap: Capturing month pattern regex
        before_pat: Before pattern regex
        after_pat: After pattern regex
        season_pat: Season pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        List of (Period, (start, end)) tuples, or None if not multi-mode
    """
    # Check if multi-mode parsing is needed
    de_date_pat = rf"(\d{{1,2}})\.\s*{mon_pat_base}\s+(\d{{3,4}})"

    multi_mode = False
    if re.search(de_date_pat, low):
        multi_mode = True
    if "(" in low or ")" in low or " - " in low:
        multi_mode = True

    if not multi_mode:
        return None

    emit_list: List[Tuple[Period, Tuple[int, int]]] = []
    used_spans: List[Tuple[int, int]] = []

    # German-style dates: "15. januar 1750"
    for m in re.finditer(rf"(\d{{1,2}})\.\s*{mon_pat_cap}\s+(\d{{3,4}})", low):
        d = int(m.group(1))
        month_tok = m.group(2)
        mm = spec.months.get(month_tok) if spec else MONTHS.get(month_tok)
        if mm is None:
            continue
        y = int(m.group(3))
        p = Period(start=(y, mm, d), end=(y, mm, d))
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # Before + season
    for m in re.finditer(
        rf"({before_pat})\s+(?:dem\s+)?({season_pat})\s+(-?\d{{3,4}})", low
    ):
        season_tok = m.group(2)
        season_name = spec.seasons.get(season_tok) if spec else season_tok
        y = int(m.group(3))
        start_m = (
            3
            if season_name == "spring"
            else 6
            if season_name == "summer"
            else 9
            if season_name == "autumn"
            else 12
        )
        if start_m == 12:
            end_y, end_m, end_d = (y - 1, 11, 30)
        else:
            end_y, end_m, end_d = (y, start_m - 1, MONTH_DAYS[start_m - 1])
        p = Period(start=(y, 1, 1), end=(end_y, end_m, end_d))
        p.express = -1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # After + season
    for m in re.finditer(
        rf"({after_pat})\s+(?:dem\s+)?({season_pat})\s+(-?\d{{3,4}})", low
    ):
        season_tok = m.group(2)
        season_name = spec.seasons.get(season_tok) if spec else season_tok
        y = int(m.group(3))
        start_m = (
            3
            if season_name == "spring"
            else 6
            if season_name == "summer"
            else 9
            if season_name == "autumn"
            else 12
        )
        end_m = start_m + 2
        if season_name == "winter":
            sy, sm, sd = (y + 1, 3, 1)
        elif end_m >= 12:
            sy, sm, sd = (y + 1, 1, 1)
        else:
            sy, sm, sd = (y, end_m + 1, 1)
        p = Period(start=(sy, sm, sd), end=(y, 12, 31))
        p.express = 1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # Before + month
    for m in re.finditer(rf"before\s+{mon_pat_cap}\s+(\d{{3,4}})", low):
        tok = m.group(1)
        mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
        if mnum is None:
            continue
        y = int(m.group(2))
        if mnum == 1:
            end_y, end_m, end_d = (y - 1, 12, 31)
        else:
            end_y, end_m, end_d = (y, mnum - 1, MONTH_DAYS[mnum - 1])
        p = Period(start=(y, 1, 1), end=(end_y, end_m, end_d))
        p.express = -1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # After + month
    for m in re.finditer(rf"after\s+{mon_pat_cap}\s+(\d{{3,4}})", low):
        tok = m.group(1)
        mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
        if mnum is None:
            continue
        y = int(m.group(2))
        sm = mnum + 1 if mnum < 12 else 12
        p = Period(start=(y, sm, 1), end=(y, 12, 31))
        p.express = 1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # Before + year
    for m in re.finditer(rf"({before_pat})\s+(-?\d{{3,4}})", low):
        y = int(m.group(2))
        p = Period(start=(y, 1, 1), end=(y - 1, 12, 31))
        p.express = -1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # After + year
    for m in re.finditer(rf"({after_pat})\s+(-?\d{{3,4}})", low):
        y = int(m.group(2))
        p = Period(start=(y + 1, 1, 1), end=(y, 12, 31))
        p.express = 1
        p.fuzzy = fuzzy
        emit_list.append((p, (m.start(), m.end())))
        used_spans.append((m.start(), m.end()))

    # Plain years not covered by keywords
    kw = rf"(?:{before_pat}|{after_pat})"
    for m in re.finditer(rf"(?:(?P<kw>{kw})\s+)?(?P<year>-?\d{{3,4}})", low):
        s, e = m.start(), m.end()
        if any(not (e <= a or s >= b) for a, b in used_spans):
            continue
        if m.group("kw"):
            continue
        y = int(m.group("year"))
        p = period_for_year(y)
        p.fuzzy = fuzzy
        emit_list.append((p, (s, e)))

    return emit_list if emit_list else None
