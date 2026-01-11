from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Set
import re
from . import resources as _res


@dataclass
class LanguageData:
    name: str


_detector = None


def _get_detector():
    global _detector
    if _detector is not None:
        return _detector
    try:
        # Use lingua for robust detection, restricted to en/de/fr
        from lingua import Language, LanguageDetectorBuilder

        _detector = (
            LanguageDetectorBuilder.from_languages(
                Language.ENGLISH, Language.GERMAN, Language.FRENCH
            )
            .with_minimum_relative_distance(0.05)
            .build()
        )
        return _detector
    except Exception:
        _detector = False  # marker to use fallback
        return _detector


def guess_language(values: Iterable[str], verbose: bool = False) -> List[str] | str:
    """Guess language for the given values.

    Prefers lingua-language-detector when available; falls back to a heuristic.
    Returns a single code ('en'|'de'|'fr') when clear, else a sorted list.
    """
    vals = [v for v in values if isinstance(v, str) and v.strip()]
    if not vals:
        raise ValueError("Could not guess language")

    # 1) Prefer explicit token presence from our language JSONs to allow multi-results
    def _json_tokens(lang: str) -> Set[str]:
        try:
            obj = _res._load_json(lang)  # type: ignore[attr-defined]
        except Exception:
            obj = None
        toks: Set[str] = set()
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, list):
                    for s in v:
                        if isinstance(s, str):
                            toks.add(s.lower())
        return toks

    tokenized_raw: Set[str] = set()
    for v in vals:
        tokenized_raw.update(re.findall(r"[\w\u00C0-\u024F\-\.]+", v.lower()))
    # Drop very short/ambiguous tokens (e.g., 'jan', 'avr', 'okt')
    tokenized = {t for t in tokenized_raw if len(t) >= 4 and not t.isdigit()}
    hits = {code: (tokenized & _json_tokens(code)) for code in ("en", "de", "fr")}
    present = [code for code, hs in hits.items() if hs]
    if present:
        if verbose:
            print(f"Guessed languages (json): {', '.join(sorted(present))}")
        return present[0] if len(present) == 1 else sorted(set(present))

    # 2) Fallback to lingua if available
    det = _get_detector()
    text = "\n".join(vals)
    if det not in (None, False):
        try:
            result = det.compute_language_confidence_values(text)
            # Sort by confidence desc
            ranked = sorted(result, key=lambda r: r.value, reverse=True)
            mapping = {"GERMAN": "de", "ENGLISH": "en", "FRENCH": "fr"}
            langs = [mapping.get(r.language.name, "") for r in ranked if r.value > 0]
            langs = [lang for lang in langs if lang]
            if verbose:
                print(
                    f"Guessed languages (lingua): {', '.join(langs) if langs else 'none'}"
                )
            if not langs:
                raise ValueError("Could not guess language")
            return (
                langs[0]
                if (len(langs) == 1 or ranked[0].value - ranked[1].value >= 0.15)
                else sorted(set(langs[:2]))
            )
        except Exception:
            # fall through to heuristic
            pass

    # Heuristic fallback
    tokens = set(re.findall(r"[\w\u00C0-\u024F\-\.]+", text.lower()))
    scores = {"de": 0, "en": 0, "fr": 0}
    de_keys = {"januar", "jahrhundert", "jh", "vor", "und", "de"}
    en_keys = {"january", "century", "bc", "after", "and", "en"}
    fr_keys = {"janvier", "siècle", "av", "jc", "et", "fr"}
    scores["de"] = len(tokens & de_keys)
    scores["en"] = len(tokens & en_keys)
    scores["fr"] = len(tokens & fr_keys)
    best = max(scores.values())
    langs = [k for k, v in scores.items() if v == best and v > 0]
    if verbose:
        print(f"Guessed languages (fallback): {', '.join(langs) if langs else 'none'}")
    if not langs:
        raise ValueError("Could not guess language")
    return langs[0] if len(langs) == 1 else sorted(set(langs))
