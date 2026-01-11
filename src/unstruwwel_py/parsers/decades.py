"""Decade parsing logic."""

from __future__ import annotations
import re
from typing import Optional

from ..dates import Period
from ..resources import LanguageSpec


def parse_decade(
    low: str, txt: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse a decade expression.

    Handles:
    - English: "1840s"
    - German: "1760er Jahre"

    Args:
        low: Lowercase input text
        txt: Original (stripped) input text
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    # decade: 1840s (en)
    m = re.fullmatch(r"(\d{3})0s", low)
    if m:
        y = int(m.group(1) + "0")
        p = Period(start=(y, 1, 1), end=(y + 9, 12, 31))
        p.fuzzy = fuzzy
        return p

    # decade (de): 1760er Jahre
    if re.search(r"er\s+jahre$", low):
        num = re.search(r"(\d{4})", low)
        if num:
            y = int(num.group(1))
            p = Period(start=(y, 1, 1), end=(y + 9, 12, 31))
            p.fuzzy = fuzzy
            return p

    return None
