"""Loading of language definitions and text standardization.

Each ``<lang>.json`` file under :mod:`unstruwwel.data` maps a language's verbal
date vocabulary (month names, "century", "half", "before", ...) onto canonical
English keys.  At import time these are compiled into regular expressions used
to (a) strip stop words and (b) replace localized terms with their canonical
key, so the downstream parser only ever sees a single, language-neutral
vocabulary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources

import regex as re

# Keys in the JSON that are not part of the replacement vocabulary.
_META_KEYS = {"name", "date_order", "stop_words", "simplifications"}

# A period that is not followed by a digit (e.g. "Jh." but not "1.5").
DOT = r"\.(?=[^0-9]|$)"

_BOUNDARY = r"[^\p{L}]"


def search_variant(term: str) -> str:
    """Build a boundary-anchored, case-insensitive-initial pattern for ``term``.

    Mirrors the R helper: only the first letter of each word is made
    case-insensitive, the term must be delimited by non-letters, and multi-word
    terms keep their internal spacing.
    """
    words = []
    for word in term.split(" "):
        if not word:
            continue
        head = word[0]
        words.append(f"[{head}{head.upper()}]{word[1:]}")
    body = " ".join(words)
    return f"(?<={_BOUNDARY}|^){body}(?={_BOUNDARY}|$)"


@dataclass
class Language:
    name: str
    date_order: str
    stop_words: list = field(default_factory=list)
    #: (compiled pattern, replacement) pairs where the term differs from its key
    replacements: list = field(default_factory=list)
    #: lowercased vocabulary, used for language detection
    vocabulary: set = field(default_factory=set)
    _remove: "re.Pattern | None" = None

    def standardize(self, text: str) -> str:
        if text is None:
            return ""
        if self._remove is not None:
            text = self._remove.sub("", text)
        text = " ".join(text.split())  # str_squish
        for pattern, after in self.replacements:
            text = pattern.sub(after, text)
        return text


def _build_language(data: dict) -> Language:
    name = data["name"].lower()
    stop_words = [w.lower() for w in data.get("stop_words", [])]

    replacements = []
    vocabulary = set()
    for key, values in data.items():
        if key in _META_KEYS:
            continue
        for value in values:
            value = value.lower()
            vocabulary.add(value)
            if value != key:
                replacements.append((re.compile(search_variant(value)), key))

    remove_patterns = [DOT] + [search_variant(w) for w in stop_words]
    remove = re.compile("|".join(remove_patterns))

    return Language(
        name=name,
        date_order=data.get("date_order", ""),
        stop_words=stop_words,
        replacements=replacements,
        vocabulary=vocabulary,
        _remove=remove,
    )


@lru_cache(maxsize=1)
def load_languages() -> dict:
    """Return a mapping of language code to :class:`Language` (cached)."""
    languages = {}
    data_dir = resources.files(__package__) / "data"
    for entry in sorted(data_dir.iterdir(), key=lambda entry: entry.name):
        if entry.name.endswith(".json"):
            data = json.loads(entry.read_text(encoding="utf-8"))
            lang = _build_language(data)
            languages[lang.name] = lang
    return languages


def is_valid_language(name) -> bool:
    return name in load_languages()
