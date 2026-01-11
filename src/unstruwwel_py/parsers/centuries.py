"""Century parsing logic."""

from __future__ import annotations
import re
from typing import Optional, Tuple

from ..dates import Period
from ..resources import LanguageSpec


def _compute_century_span(
    century: int, part: Optional[int], part_type: Optional[str], bce: bool
) -> Tuple[int, int]:
    """Compute the year span for a century or part thereof.

    Args:
        century: Century number (1-21)
        part: Which part (1, 2, 3, or 4) - None for full century
        part_type: 'half', 'third', 'quarter', or None
        bce: Whether this is BCE

    Returns:
        (start_year, end_year) tuple
    """
    if bce:
        base_start = -100 * century
        base_end = -(100 * (century - 1) + 1)
    else:
        base_start = 100 * (century - 1) + 1
        base_end = 100 * century

    if part_type is None or part is None:
        return (base_start, base_end)

    # Calculate fractional spans
    span = base_end - base_start + 1  # 100 years

    if part_type == "half":
        half_size = span // 2
        if part == 1:
            return (base_start, base_start + half_size - 1)
        else:
            return (base_start + half_size, base_end)
    elif part_type == "third":
        third_size = span // 3
        if part == 1:
            return (base_start, base_start + third_size - 1)
        elif part == 2:
            return (base_start + third_size, base_start + 2 * third_size - 1)
        else:
            return (base_start + 2 * third_size, base_end)
    elif part_type == "quarter":
        quarter_size = span // 4
        if part == 1:
            return (base_start, base_start + quarter_size - 1)
        elif part == 2:
            return (base_start + quarter_size, base_start + 2 * quarter_size - 1)
        elif part == 3:
            return (base_start + 2 * quarter_size, base_start + 3 * quarter_size - 1)
        else:
            return (base_start + 3 * quarter_size, base_end)

    return (base_start, base_end)


def parse_century(
    low: str, spec: Optional[LanguageSpec], fuzzy: int
) -> Optional[Period]:
    """Try to parse a century expression using language spec patterns.

    Args:
        low: Lowercase input text
        spec: Language specification
        fuzzy: Fuzzy marker (-1 = approximate, 0 = exact, 1 = uncertain)

    Returns:
        Period if matched, None otherwise
    """
    if not spec:
        return None

    century_pat = spec.century_pattern()
    if not century_pat:
        return None

    bc_pat = spec.bc_pattern()
    ordinal_pat = spec.ordinal_pattern()
    half_pat = spec.half_pattern()
    third_pat = spec.third_pattern()
    quarter_pat = spec.quarter_pattern()

    # Check for approximate marker
    is_approx = any(k in low for k in spec.approximate)

    # Try fractional century pattern
    frac_patterns = []
    if half_pat:
        frac_patterns.append((half_pat, "half", 2))
    if third_pat:
        frac_patterns.append((third_pat, "third", 3))
    if quarter_pat:
        frac_patterns.append((quarter_pat, "quarter", 4))

    for frac_pat, frac_type, max_part in frac_patterns:
        # Pattern: [approx] [ordinal] [fraction] [ordinal] [century] [bc]
        pattern = rf"(?:ca\.?\s+)?({ordinal_pat})?\s*({frac_pat})\s+({ordinal_pat})\s*\.?\s*({century_pat})\.?\s*({bc_pat})?"
        m = re.search(pattern, low, re.IGNORECASE)
        if m:
            part_str = m.group(1)
            century_str = m.group(3)
            bce = bool(m.group(5))

            part = spec.parse_ordinal(part_str) if part_str else 1
            century = spec.parse_ordinal(century_str)

            if century and part and 1 <= part <= max_part:
                # Check for "last" modifier
                for last_tok in spec.last_tokens:
                    if last_tok in low:
                        part = max_part
                        break

                start, end = _compute_century_span(century, part, frac_type, bce)
                if bce:
                    p = Period(start=(start, 12, 31), end=(end, 1, 1))
                else:
                    p = Period(start=(start, 1, 1), end=(end, 12, 31))
                p.fuzzy = -1 if is_approx else fuzzy
                return p

    # Try simple century pattern: "[ordinal] century [bc]"
    pattern = rf"({ordinal_pat})\s*\.?\s*({century_pat})\.?\s*({bc_pat})?"
    m = re.search(pattern, low, re.IGNORECASE)
    if m:
        century_str = m.group(1)
        bce = bool(m.group(3))
        century = spec.parse_ordinal(century_str)

        if century:
            start, end = _compute_century_span(century, None, None, bce)
            if bce:
                p = Period(start=(start, 12, 31), end=(end, 1, 1))
            else:
                p = Period(start=(start, 1, 1), end=(end, 12, 31))
            p.fuzzy = -1 if is_approx else fuzzy
            return p

    return None
