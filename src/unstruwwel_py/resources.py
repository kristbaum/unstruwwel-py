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
        # Allow punctuation/whitespace variants by converting spaces to optional punctuation+spaces
        parts = []
        for tok in self.bc_markers:
            # normalize multiple spaces
            t = re.sub(r"\s+", "\\s*", tok)
            parts.append(re.escape(tok).replace("\\ ", "\\s*"))
        alt = "|".join(parts)
        return f"(?:{alt})"


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
    )


def get_language_spec(lang: str) -> Optional[LanguageSpec]:
    lang = lang.lower()
    if lang in {"de", "fr"}:
        obj = _load_json(lang)
        if obj is None:
            return None
        return _build_spec_from_json(obj)
    # For English, synthesize from built-in constants in dates.py
    if lang == "en":
        from .dates import MONTHS

        months = {name: num for name, num in MONTHS.items()}
        seasons = {
            "winter": "winter",
            "spring": "spring",
            "summer": "summer",
            "autumn": "autumn",
        }
        before = {"before"}
        after = {"after"}
        uncertain = {"uncertain", "perhaps", "probably"}
        approximate = {"circa", "ca", "ca.", "around", "about"}
        decade_suffixes: Set[str] = {"s"}
        bc_markers: Set[str] = {"bc", "bce"}
        and_tokens: Set[str] = {"and", "-"}
        return LanguageSpec(
            "en",
            months,
            seasons,
            before,
            after,
            uncertain,
            approximate,
            decade_suffixes,
            bc_markers,
            and_tokens,
        )
    return None
