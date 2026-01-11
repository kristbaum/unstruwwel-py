# unstruwwel-py

Python port of the R package “unstruwwel”: detect and parse historic dates into ISO 8601-like representations.

- Parse years, months, seasons, decades, centuries, ranges, and fuzzy markers
- Multi-language support (en, de, fr) with resource-driven tokens
- Language guessing with fallback to heuristic
- Object and value-oriented outputs

## Installation

Inside this repository (editable install):

```bash
# in your venv
pip install -e .[dev]
```

## Quick start

```python
from unstruwwel_py import unstruwwel

# Basic parsing (default scheme="time-span")
unstruwwel(["1840s", "after March 1755", "Winter 1620", "19. Jh."])
# => [ (1840, 1849), (1756, 1755)  # open interval encoded as (start,end)
#      (1620.12.01, 1621.02.28), (1801, 1900) ]

# ISO-like string output
unstruwwel(["March 1755"], scheme="iso-format")
# => ["1755-03"]

# Object output requires language
from unstruwwel_py import Year, Decade, Century
unstruwwel(["1755", "1840s", "19. Jh."], language="de", scheme="object")
# => [Parsed(... Period(year=1755) ...), Parsed(... Decade(1840) ...), Parsed(... Century(19) ...)]
```

## API

- unstruwwel(texts, language=None, scheme="time-span") -> list
  - texts: str | list[str | None]
  - language: 'en' | 'de' | 'fr' (required for scheme='object')
  - scheme: 'time-span' | 'iso-format' | 'object'
  - returns list of results per input item:
    - time-span: (start, end)
    - iso-format: string (e.g., "1755-03", "1620-Wi")
    - object: Parsed dataclass wrapping a Period-like payload

- get_item(x, i=1) -> any
  - R-like 1-based indexing helper

- Year(year: int).take(...)
- Decade(decade: int).take(part=None, type=None, ignore_errors=False)
- Century(century: int | str).take(part=None, type=None, ignore_errors=False)
  - type: 'half' | 'third' | 'quarter' | 'early' | 'mid' | 'late'
  - part: 1..n depending on type or 'last' for the last fraction

- guess_language(values: Iterable[str], verbose=False) -> 'en'|'de'|'fr' | list[str]
  - Returns a single language code for clear cases; a list of codes when ambiguous (e.g., ["en","fr"]).

## Features supported

- unknown markers -> NA span
- month + year; before/after month + year (language-specific)
- seasons with winter cross-year handling
- short ranges like 1752/60
- decades: "1840s" (en), "1760er Jahre" (de)
- centuries: "19. Jh." (de), English forms like "18th century"; fractional parts (half/third/quarter), early/mid/late
- fuzzy markers: approximate (~, circa) and uncertain
- multi-extraction within a single string and overlap avoidance

## Examples

```python
from unstruwwel_py import unstruwwel

texts = [
    "1752/60",
    "before April 1755",
    "nach Frühling 1755",
    "Winter 1620",
    "last third 17th century",
]
print(unstruwwel(texts))
```

## CLI snippet (optional)

```bash
python - <<'PY'
from unstruwwel_py import unstruwwel
print(unstruwwel(["1840s", "19. Jh.", "March 1755"]))
PY
```

## Development

- Run tests:

```bash
pytest -q
```

- Lint:

```bash
ruff check
```

## Troubleshooting

- If language is omitted with scheme='object', ValueError is raised.
- Mixed-language content may return multiple codes from guess_language.
- Ensure your venv has the dependency 'lingua-language-detector' if you use language guessing.

## License

MIT
