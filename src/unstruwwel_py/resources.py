from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set


@dataclass
class LanguageSpec:
    name: str
    months: Dict[str, int]  # token -> month number
    seasons: Dict[str, str]  # token -> canonical season (spring/summer/autumn/winter)
    before: Set[str]
    after: Set[str]
    uncertain: Set[str]
    approximate: Set[str]
    decade_suffixes: Set[str]
    bc_markers: Set[str]
    and_tokens: Set[str]
    century_tokens: Set[str]  # e.g., {"century", "cent", "jh", "jahrhundert"}
    half_tokens: Set[str]  # e.g., {"half", "hälfte"}
    third_tokens: Set[str]  # e.g., {"third", "drittel"}
    quarter_tokens: Set[str]  # e.g., {"quarter", "viertel"}
    last_tokens: Set[str]  # e.g., {"last", "letztes"}
    ordinals: Dict[str, int]  # e.g., {"first": 1, "erste": 1, ...}
    early_tokens: Set[str]  # e.g., {"early", "anfang"}
    mid_tokens: Set[str]  # e.g., {"mid", "mitte"}
    late_tokens: Set[str]  # e.g., {"late", "ende"}

    def month_pattern(self) -> str:
        if not self.months:
            return ""
        # Longest-first to avoid partial matching (e.g., mär vs märz)
        toks = sorted(self.months.keys(), key=len, reverse=True)
        alt = "|".join(re.escape(t) for t in toks)
        return f"(?:{alt})"

    def season_pattern(self) -> str:
        if not self.seasons:
            return ""
        toks = sorted(self.seasons.keys(), key=len, reverse=True)
        alt = "|".join(re.escape(t) for t in toks)
        return f"(?:{alt})"

    def before_pattern(self) -> str:
        if not self.before:
            return ""
        alt = "|".join(re.escape(t) for t in sorted(self.before, key=len, reverse=True))
        return f"(?:{alt})"

    def after_pattern(self) -> str:
        if not self.after:
            return ""
        alt = "|".join(re.escape(t) for t in sorted(self.after, key=len, reverse=True))
        return f"(?:{alt})"

    def bc_pattern(self) -> str:
        if not self.bc_markers:
            return ""
        # Build pattern allowing optional whitespace/punctuation between words
        parts = []
        for tok in self.bc_markers:
            # Replace spaces with \s* and add optional dots after each word
            words = tok.split()
            escaped_words = [re.escape(w) + r"\.?" for w in words]
            parts.append(r"\s*".join(escaped_words))
        alt = "|".join(parts)
        return f"(?:{alt})"

    def century_pattern(self) -> str:
        if not self.century_tokens:
            return ""
        alt = "|".join(
            re.escape(t) for t in sorted(self.century_tokens, key=len, reverse=True)
        )
        return f"(?:{alt})"

    def half_pattern(self) -> str:
        if not self.half_tokens:
            return ""
        alt = "|".join(
            re.escape(t) for t in sorted(self.half_tokens, key=len, reverse=True)
        )
        return f"(?:{alt})"

    def third_pattern(self) -> str:
        if not self.third_tokens:
            return ""
        alt = "|".join(
            re.escape(t) for t in sorted(self.third_tokens, key=len, reverse=True)
        )
        return f"(?:{alt})"

    def quarter_pattern(self) -> str:
        if not self.quarter_tokens:
            return ""
        alt = "|".join(
            re.escape(t) for t in sorted(self.quarter_tokens, key=len, reverse=True)
        )
        return f"(?:{alt})"

    def ordinal_pattern(self) -> str:
        """Pattern matching ordinal words like 'first', 'erste', or numeric ordinals like '1.' '2nd'"""
        parts = []
        # Word ordinals from the dict
        if self.ordinals:
            parts.extend(
                re.escape(t)
                for t in sorted(self.ordinals.keys(), key=len, reverse=True)
            )
        # Numeric ordinals: 1., 2., etc. (German style) and 1st, 2nd, 3rd, 4th (English style)
        parts.append(r"\d+\.")
        parts.append(r"\d+(?:st|nd|rd|th)")
        return f"(?:{'|'.join(parts)})"

    def parse_ordinal(self, tok: str) -> Optional[int]:
        """Parse an ordinal token to its numeric value."""
        tok = tok.lower().strip()
        if tok in self.ordinals:
            return self.ordinals[tok]
        # Try numeric forms: "1.", "2nd", etc.
        m = re.match(r"(\d+)(?:\.|st|nd|rd|th)?$", tok)
        if m:
            return int(m.group(1))
        return None


def _base_dir() -> Path:
    # project root = .../unstruwwel
    return Path(__file__).resolve().parents[2]


def _load_json(name: str) -> Optional[dict]:
    path = _base_dir() / "data-raw" / f"{name}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_spec_from_json(obj: dict) -> LanguageSpec:
    months: Dict[str, int] = {}
    month_order = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    for i, key in enumerate(month_order, start=1):
        for tok in obj.get(key, []):
            months[tok.lower()] = i
    seasons: Dict[str, str] = {}
    for sname in ["winter", "spring", "summer", "autumn"]:
        for tok in obj.get(sname, []):
            seasons[tok.lower()] = sname
    before = set(t.lower() for t in obj.get("before", []))
    after = set(t.lower() for t in obj.get("after", []))
    uncertain = set(t.lower() for t in obj.get("uncertain", []))
    approximate = set(t.lower() for t in obj.get("approximate", [])) or set(
        obj.get("circa", [])
    )
    decade_suffixes = set(t.lower() for t in obj.get("s", []))
    bc_markers = set(t.lower() for t in obj.get("bc", []))
    and_tokens = set(t.lower() for t in obj.get("and", []))
    century_tokens = set(t.lower() for t in obj.get("century", []))
    half_tokens = set(t.lower() for t in obj.get("half", []))
    third_tokens = set(t.lower() for t in obj.get("third", []))
    quarter_tokens = set(t.lower() for t in obj.get("quarter", []))
    last_tokens = set(t.lower() for t in obj.get("last", []))
    early_tokens = set(t.lower() for t in obj.get("early", []))
    mid_tokens = set(t.lower() for t in obj.get("mid", []))
    late_tokens = set(t.lower() for t in obj.get("late", []))
    # Build ordinals from simplifications
    ordinals: Dict[str, int] = {}
    for word, num in obj.get("simplifications", {}).items():
        try:
            ordinals[word.lower()] = int(num)
        except (ValueError, TypeError):
            pass
    return LanguageSpec(
        name=obj.get("name", ""),
        months=months,
        seasons=seasons,
        before=before,
        after=after,
        uncertain=uncertain,
        approximate=approximate,
        decade_suffixes=decade_suffixes,
        bc_markers=bc_markers,
        and_tokens=and_tokens,
        century_tokens=century_tokens,
        half_tokens=half_tokens,
        third_tokens=third_tokens,
        quarter_tokens=quarter_tokens,
        last_tokens=last_tokens,
        ordinals=ordinals,
        early_tokens=early_tokens,
        mid_tokens=mid_tokens,
        late_tokens=late_tokens,
    )


def get_language_spec(lang: str) -> Optional[LanguageSpec]:
    lang = lang.lower()
    if lang in {"de", "fr", "en"}:
        obj = _load_json(lang)
        if obj is None:
            return None
        return _build_spec_from_json(obj)
    return None
