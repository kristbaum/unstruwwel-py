"""Season parsing logic."""

from __future__ import annotations
import re
from typing import Optional

from ..dates import Period, period_for_season
from ..resources import LanguageSpec


def parse_season(
    low: str, sp_cap: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse season + year expression.

    Args:
        low: Lowercase input text
        sp_cap: Capturing season pattern regex
        spec: Language specification
        fuzzy: Fuzzy marker

    Returns:
        Period if matched, None otherwise
    """
    m = re.fullmatch(rf"{sp_cap}\s+(\d{{3,4}})", low)
    if m:
        season_tok = m.group(1)
        season = spec.seasons.get(season_tok) if spec else season_tok
        if not isinstance(season, str):
            season = "winter"
        y = int(m.group(2))
        p = period_for_season(y, season)
        p.fuzzy = fuzzy
        return p
    return None


def season_start_month(season: str) -> int:
    """Return the starting month for a canonical season name."""
    return {"spring": 3, "summer": 6, "autumn": 9, "winter": 12}.get(season, 12)
