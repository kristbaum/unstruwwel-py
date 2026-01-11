from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Any, List, Optional, Sequence, Tuple, Union

from .dates import (
    Period,
    period_for_year,
    period_for_month,
    period_for_season,
    MONTHS,
    MONTH_DAYS,
)
from .resources import get_language_spec
from .lang import guess_language


@dataclass
class Parsed:
    text: str
    time_span: Tuple[Optional[float], Optional[float]]
    iso_format: Optional[str]
    fuzzy: int = 0  # -1 = approximate, 0 = exact, 1 = uncertain


Result = Union[Parsed, Tuple[Optional[float], Optional[float]]]


def get_item(x: Sequence[Any], i: int = 1) -> Any:
    """R-like helper to fetch the i-th item (1-based)."""
    idx = i - 1
    return x[idx]


def unstruwwel(
    texts: Optional[Union[str, Sequence[Optional[str]]]],
    language: Optional[str] = None,
    scheme: str = "time-span",
) -> List[Result]:
    """Parse historic dates (subset) into time spans, iso-format, or objects.

    Supported (first pass):
    - unknown/undatiert -> NA
    - plain year (incl. negatives) -> full-year span
    - month name + year (English) -> month span
    - seasons in English/German keywords -> season span
    - before/after + (month?) year -> open-ended intervals
    - year interval like 1752/60 -> 1752..1760
    - decade forms: '1840s' (en), '1760er Jahre' (de)
    - simple centuries: '19. Jh.' (de), '5. Jh. v. Chr', 'last third 17th cent' (en minimal)
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
        # placeholder: unknown => NA
        if t is None or (
            isinstance(t, str) and t.strip().lower() in {"undatiert", "unknown"}
        ):
            if scheme == "object":
                out.append(
                    Parsed(
                        text=t or "", time_span=(None, None), iso_format=None, fuzzy=0
                    )
                )
            else:
                out.append((None, None))
            continue

        txt = t.strip()
        lang = language
        if lang is None:
            try:
                gl = guess_language([txt], verbose=False)
                lang = gl if isinstance(gl, str) else gl[0]
            except Exception:
                lang = "en"

        # Precompute lowercase and fuzzy markers
        low = txt.lower()
        spec = get_language_spec(lang) if lang else None
        fuzzy = 0
        if spec and any(k in low for k in spec.approximate):
            fuzzy = -1
        elif any(k in low for k in ["circa", "ca", "ca."]):
            fuzzy = -1
        if spec and any(k in low for k in spec.uncertain):
            fuzzy = 1
        elif any(k in low for k in ["uncertain", "perhaps", "probably"]):
            fuzzy = 1

        # Month/season patterns
        mon_pat_base = (
            spec.month_pattern()
            if spec
            else r"(?:january|february|march|april|may|june|july|august|september|october|november|december)"
        )
        mon_pat_cap = f"({mon_pat_base})"
        sp_base = spec.season_pattern() if spec else r"(?:spring|summer|autumn|winter)"
        sp_cap = f"({sp_base})"

        # Multi-extraction
        emit_list: List[Result] = []
        used_spans: List[Tuple[int, int]] = []

        # Build before/after patterns from spec
        before_pat = spec.before_pattern() if spec else r"(?:before)"
        after_pat = spec.after_pattern() if spec else r"(?:after)"
        season_pat = (
            spec.season_pattern() if spec else r"(?:spring|summer|autumn|winter)"
        )

        # Pattern for day.month year (e.g., "15. januar 1750")
        de_date_pat = rf"(\d{{1,2}})\.\s*{mon_pat_base}\s+(\d{{3,4}})"

        multi_mode = False
        if re.search(de_date_pat, low):
            multi_mode = True
        if "(" in low or ")" in low or " - " in low:
            multi_mode = True
        if multi_mode:
            for m in re.finditer(rf"(\d{{1,2}})\.\s*{mon_pat_cap}\s+(\d{{3,4}})", low):
                d = int(m.group(1))
                month_tok = m.group(2)
                mm = spec.months.get(month_tok) if spec else MONTHS.get(month_tok)
                if mm is None:
                    continue
                y = int(m.group(3))
                p = Period(start=(y, mm, d), end=(y, mm, d))
                p.fuzzy = fuzzy
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))

            for m in re.finditer(
                rf"({before_pat})\s+(?:dem\s+)?({season_pat})\s+(-?\d{{3,4}})",
                low,
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
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))
            for m in re.finditer(
                rf"({after_pat})\s+(?:dem\s+)?({season_pat})\s+(-?\d{{3,4}})",
                low,
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
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))

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
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))
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
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))
            for m in re.finditer(rf"({before_pat})\s+(-?\d{{3,4}})", low):
                y = int(m.group(2))
                p = Period(start=(y, 1, 1), end=(y - 1, 12, 31))
                p.express = -1
                p.fuzzy = fuzzy
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))
            for m in re.finditer(rf"({after_pat})\s+(-?\d{{3,4}})", low):
                y = int(m.group(2))
                p = Period(start=(y + 1, 1, 1), end=(y, 12, 31))
                p.express = 1
                p.fuzzy = fuzzy
                emit_list.append(_emit(p, scheme))
                used_spans.append((m.start(), m.end()))

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
                emit_list.append(_emit(p, scheme))
            if emit_list:
                out.extend(emit_list)
                continue

        # decade: 1840s (en)
        m = re.fullmatch(r"(\d{3})0s", low)
        if m:
            y = int(m.group(1) + "0")
            p = Period(start=(y, 1, 1), end=(y + 9, 12, 31))
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # decade (de): 1760er Jahre
        if re.search(r"er\s+jahre$", low):
            num = re.search(r"(\d{4})", low)
            if num:
                y = int(num.group(1))
                p = Period(start=(y, 1, 1), end=(y + 9, 12, 31))
                p.fuzzy = fuzzy
                out.append(_emit(p, scheme))
                continue

        # year interval short 1752/60
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
            out.append(_emit(p, scheme))
            continue

        # before/after month-year or year (English and German)
        expr = 0
        # Check if text starts with a "before" keyword
        before_keywords = spec.before if spec else {"before"}
        after_keywords = spec.after if spec else {"after"}
        for kw in before_keywords:
            if low.startswith(kw):
                expr = -1
                break
        if expr == 0:
            for kw in after_keywords:
                if low.startswith(kw):
                    expr = 1
                    break
        if expr != 0:
            ym = re.findall(mon_pat_cap, low)
            m_season = re.search(rf"({season_pat})", low) if spec else None
            season_tok = m_season.group(1) if m_season else None
            season_name = spec.seasons.get(season_tok) if spec and season_tok else None
            yx = re.findall(r"(-?\d{3,4})", low)
            if yx:
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
                    out.append(_emit(p, scheme))
                    continue
                if ym:
                    mname = ym[-1]
                    mnum = spec.months.get(mname) if spec else MONTHS.get(mname)
                    if mnum:
                        if expr < 0:
                            if mnum == 1:
                                end_y, end_m, end_d = (y - 1, 12, 31)
                            else:
                                end_y, end_m, end_d = (
                                    y,
                                    mnum - 1,
                                    MONTH_DAYS[mnum - 1],
                                )
                            p = Period(start=(y, 1, 1), end=(end_y, end_m, end_d))
                            p.express = -1
                        else:
                            start_mn = mnum + 1 if mnum < 12 else 12
                            p = Period(start=(y, start_mn, 1), end=(y, 12, 31))
                            p.express = 1
                        p.fuzzy = fuzzy
                        out.append(_emit(p, scheme))
                        continue
                else:
                    if expr < 0:
                        p = Period(start=(y, 1, 1), end=(y - 1, 12, 31))
                        p.express = -1
                    else:
                        p = Period(start=(y + 1, 1, 1), end=(y, 12, 31))
                        p.express = 1
                    p.fuzzy = fuzzy
                    out.append(_emit(p, scheme))
                    continue

        # season + year
        m = re.fullmatch(rf"{sp_cap}\s+(\d{{3,4}})", low)
        if m:
            season_tok = m.group(1)
            season = spec.seasons.get(season_tok) if spec else season_tok  # type: ignore[assignment]
            if not isinstance(season, str):
                season = "winter"
            y = int(m.group(2))
            p = period_for_season(y, season)
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # month + year
        m = re.fullmatch(rf"{mon_pat_cap}\s+(\d{{3,4}})", low)
        if m:
            y = int(m.group(2))
            tok = m.group(1)
            mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
            if mnum is not None:
                p = period_for_month(y, mnum)
                p.fuzzy = fuzzy
                out.append(_emit(p, scheme))
                continue

        # exact day Month D, YYYY (English)
        m = re.fullmatch(rf"{mon_pat_cap}\s+(\d{{1,2}}),\s*(\d{{3,4}})", low)
        if m:
            y = int(m.group(3))
            d = int(m.group(2))
            tok = m.group(1)
            mnum = spec.months.get(tok) if spec else MONTHS.get(tok)
            if mnum is not None:
                p = Period(start=(y, mnum, d), end=(y, mnum, d))
                p.fuzzy = fuzzy
                out.append(_emit(p, scheme))
                continue

        # centuries (simple): "19. Jh." (de)
        if re.fullmatch(r"\s*\d{1,2}\.\s*jh\.?", low):
            mnum = re.search(r"\d+", low)
            assert mnum is not None
            c = int(mnum.group(0))
            start = 100 * (c - 1) + 1
            end = 100 * c
            p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # german half centuries
        m = re.fullmatch(
            r"(ca\.?\s+)?(1\.|erste)\s*h(ä|ae)lfte\s+(\d{1,2})\.\s*jh(\.?)\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(4))
            bce = bool(m.group(6))
            if bce:
                start = -100 * c
                end = -(100 * (c - 1) + 51)
            else:
                start = 100 * (c - 1) + 1
                end = start + 49
            p = Period(
                start=(start, 1, 1) if not bce else (start, 12, 31),
                end=(end, 12, 31) if not bce else (end, 1, 1),
            )
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?(2\.|zweite)\s*h(ä|ae)lfte\s+(\d{1,2})\.\s*jh(\.?)\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(4))
            bce = bool(m.group(6))
            if bce:
                start = -(100 * (c - 1) + 50)
                end = -(100 * (c - 1) + 1)
            else:
                start = 100 * (c - 1) + 50
                end = 100 * c
            p = Period(
                start=(start, 1, 1) if not bce else (start, 12, 31),
                end=(end, 12, 31) if not bce else (end, 1, 1),
            )
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue

        # centuries (BCE)
        if re.search(r"jh\..*v\.?\s*chr", low):
            mnum = re.search(r"\d+", low)
            assert mnum is not None
            c = int(mnum.group(0))
            start_y = -100 * c
            end_y = -(100 * (c - 1) + 1)
            p = Period(start=(start_y, 12, 31), end=(end_y, 1, 1))
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # german: thirds/quarters of centuries
        m = re.fullmatch(
            r"(ca\.?\s+)?(1\.|erste|erstes)\s*drittel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(3))
            bce = bool(m.group(4))
            if bce:
                start = -100 * c
                end = -(100 * (c - 1) + 68)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 1
                end = start + 32
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?(2\.|zweite|zweites)\s*drittel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(3))
            bce = bool(m.group(4))
            if bce:
                start = -(100 * (c - 1) + 67)
                end = -(100 * (c - 1) + 35)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 33
                end = 100 * (c - 1) + 65
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?((3\.|dritte|drittes)|letzte(s)?)\s*drittel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(5))
            bce = bool(m.group(6))
            if bce:
                start = -(100 * (c - 1) + 34)
                end = -(100 * (c - 1) + 1)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 66
                end = 100 * c
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue

        m = re.fullmatch(
            r"(ca\.?\s+)?(1\.|erste|erstes)\s*viertel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(3))
            bce = bool(m.group(4))
            if bce:
                start = -100 * c
                end = -(100 * (c - 1) + 76)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 1
                end = start + 24
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?(2\.|zweite|zweites)\s*viertel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(3))
            bce = bool(m.group(4))
            if bce:
                start = -(100 * (c - 1) + 75)
                end = -(100 * (c - 1) + 51)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 25
                end = 100 * (c - 1) + 49
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?(3\.|dritte|drittes)\s*viertel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(3))
            bce = bool(m.group(4))
            if bce:
                start = -(100 * (c - 1) + 50)
                end = -(100 * (c - 1) + 26)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 50
                end = 100 * (c - 1) + 74
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue
        m = re.fullmatch(
            r"(ca\.?\s+)?((4\.|viertes|letzte(s)?))\s*viertel\s+(\d{1,2})\.\s*jh\.?\s*(v\.?\s*chr)?",
            low,
        )
        if m:
            c = int(m.group(5))
            bce = bool(m.group(6))
            if bce:
                start = -(100 * (c - 1) + 25)
                end = -(100 * (c - 1) + 1)
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                start = 100 * (c - 1) + 75
                end = 100 * c
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue

        # english: last third 17th cent
        if re.fullmatch(r"last\s+third\s+\d{1,2}(st|nd|rd|th)\s+cent(ury)?", low):
            mnum = re.search(r"\d+", low)
            assert mnum is not None
            c = int(mnum.group(0))
            start = 100 * (c - 1) + 67
            end = 100 * c
            p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # english centuries like '18th century'
        m = re.fullmatch(r"(circa\s+)?(\d{1,2})(st|nd|rd|th)\s+cent(ury)?", low)
        if m:
            c = int(m.group(2))
            start = 100 * (c - 1) + 1
            end = 100 * c
            p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if m.group(1) else fuzzy
            out.append(_emit(p, scheme))
            continue

        # plain year
        m = re.fullmatch(r"(-?\d{3,4})", txt)
        if m:
            y = int(m.group(1))
            p = period_for_year(y)
            p.fuzzy = fuzzy
            out.append(_emit(p, scheme))
            continue

        # fallback
        if scheme == "object":
            out.append(
                Parsed(
                    text=t or "", time_span=(None, None), iso_format=None, fuzzy=fuzzy
                )
            )
        else:
            out.append((None, None))
    return out


def _emit(p: Period, scheme: str) -> Result:
    if scheme == "time-span":
        return (p.time_span[0], p.time_span[1])
    if scheme == "iso-format":
        return p.iso_format  # type: ignore[return-value]
    # object
    return Parsed(
        text="", time_span=p.time_span, iso_format=p.iso_format, fuzzy=p.fuzzy
    )
