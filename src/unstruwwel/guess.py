"""Heuristics for detecting the input language and MIDAS standardization."""

from __future__ import annotations

from typing import List

import regex as re

from .languages import load_languages

_WORD = re.compile(r"\p{L}{3,}")  # at least three letters
_DIGIT = re.compile(r"[0-9]")


def guess_language(texts, verbose: bool = True) -> List[str]:
    """Detect the dominant language(s) of ``texts``.

    For every entry that mixes letters and digits, the language whose
    vocabulary covers the most of its words scores a point (ties score
    nothing).  Languages with more than half the leader's points are returned.
    """
    languages = load_languages()
    candidates = [
        t for t in texts if t and _DIGIT.search(t) and _WORD.search(t)
    ]

    wins = {name: 0 for name in languages}
    for text in candidates:
        words = {w.lower() for w in _WORD.findall(text)}
        counts = {
            name: len(words & lang.vocabulary)
            for name, lang in languages.items()
        }
        best = max(counts.values())
        if best == 0:
            continue
        leaders = [name for name, c in counts.items() if c == best]
        if len(leaders) == 1:
            wins[leaders[0]] += 1

    if not any(wins.values()):
        raise ValueError("Language could not be detected.")

    threshold = max(wins.values()) / 2
    detected = sorted(name for name, w in wins.items() if w > threshold)

    if verbose:
        print(
            "The following languages have been detected: "
            f"{', '.join(detected)}."
        )
    return detected


def guess_midas(texts, midas: bool = False, verbose: bool = True) -> bool:
    """Warn if ``texts`` look like they were already MIDAS-standardized."""
    n = len(texts)
    if n == 0:
        return midas

    count_slash = sum(1 for t in texts if t and "/" in t) / n
    dashes = [chr(c) for c in range(0x2010, 0x2016)] + ["-"]
    count_dash = sum(
        1 for t in texts if t and any(d in t for d in dashes)
    ) / n

    if count_dash - count_slash < -0.15 and not midas:
        if verbose:
            print(
                "Please check if input vector might have been "
                "standardized using MIDAS."
            )
    return midas
