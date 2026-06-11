# unstruwwel-py

Detect and parse historic dates, e.g. to ISO 8601:2-2019.

This is a Python port of the R package
[unstruwwel](https://github.com/stefanieschneider/unstruwwel). It automatically
converts language-specific verbal information, e.g. *"circa 1st half of the
19th century"*, into its standardized numerical counterparts, e.g.
*"1801-01-01~/1850-12-31~"*. It follows the recommendations of the MIDAS
(Marburger Informations-, Dokumentations- und Administrations-System); see
<https://doi.org/10.11588/artdok.00003770>.

The name is inspired by Heinrich Hoffmann's rhymed story
[*Struwwelpeter*](https://www.gutenberg.org/files/12116/12116-h/12116-h.htm).

## Installation

```bash
pip install unstruwwel-py
```

Or, for local development with [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -e ".[dev]"
```

## Usage

The package exposes a single high-level function, `unstruwwel()`. Pass a string
or an iterable of strings; for an iterable a list of results is returned, one
per input.

### Schemes

- `"time-span"` (default) — a `(start, end)` tuple of years. Open intervals use
  `math.inf` / `-math.inf`; an undetectable date yields `(None, None)`.
- `"iso-format"` — an ISO 8601:2-2019 string (or `None`).
- `"object"` — a list of `Periods` objects, each exposing `.time_span`,
  `.iso_format`, `.interval`, `.fuzzy`, and `.express`.

### Safe vs. aggressive mode

Many real-world entries list several *distinct* datings rather than one period,
e.g. `"1184, 1750-1752"` or `"1070-1129, 1672-1674, 1938-1940"`. Collapsing
those into a single `(1184, 1752)` span is misleading, so the default
`mode="safe"` declines to resolve a compound entry and returns the empty result
instead:

```python
unstruwwel("1184, 1750-1752", "de")                       # (None, None)
unstruwwel("1184, 1750-1752", "de", mode="aggressive")    # (1184, 1752)
```

A single period — including ranges like `"1750-1752"`, `"1443 bis 1640"`, or
`"16. Jhd. - 18. Jhd."` — resolves under both modes. Use `mode="aggressive"`
when you want a best-effort enclosing span for every entry.

### English-language examples

```python
from unstruwwel import unstruwwel

dates = [
    "5th century b.c.", "unknown", "late 16th century", "mid-12th century",
    "June 1963", "August 11, 1958", "ca. 1920", "before 1856",
]

unstruwwel(dates, "en", scheme="iso-format")
# ['-0500-12-31/-0401-01-01', None, '1586-01-01/1600-12-31',
#  '1146-01-01/1155-12-31', '1963-06-01/1963-06-30',
#  '1958-08-11/1958-08-11', '1920-01-01~/1920-12-31~', '..1855-12-31']

unstruwwel(dates, "en")  # time-span
# [(-500, -401), (None, None), (1586, 1600), (1146, 1155),
#  (1963, 1963), (1958, 1958), (1920, 1920), (-inf, 1855)]
```

### German-language examples

```python
unstruwwel("letztes Drittel 15. und 1. Hälfte 16. Jahrhundert", "de")
# (1467, 1550)

unstruwwel("wohl nach 1923", "de", scheme="iso-format")
# '1924-01-01?..'

unstruwwel("spätestens 1750er Jahre", "de", scheme="iso-format")
# '..1749-12-31'
```

### Processing a CSV column

A common use case is resolving a whole column of verbal datings, e.g. harvested
from a museum or research database. Pass the column as an iterable and you get
one result per row back, aligned with the input. The snippet below reads a
`verbaleDating` column, resolves it under both schemes, and writes a new CSV
that places the original text next to its `start`/`end` years and ISO string
for easy comparison:

```python
import csv
from unstruwwel import unstruwwel

with open("verbal_dating.csv", encoding="utf-8") as f:
    rows = [row["verbaleDating"] for row in csv.DictReader(f)]

spans = unstruwwel(rows, "de")                       # [(start, end), ...]
iso = unstruwwel(rows, "de", scheme="iso-format")    # ['1746-01-01/...', ...]

with open("verbal_dating_resolved.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["verbaleDating", "start", "end", "iso"])
    for text, (start, end), iso_str in zip(rows, spans, iso):
        writer.writerow([text, start, end, iso_str])
```

For the real *Deckenmalerei* entries below, `verbal_dating_resolved.csv` then
contains:

| verbaleDating | start | end | iso |
| --- | --- | --- | --- |
| `um 1750` | `1750` | `1750` | `1750-01-01~/1750-12-31~` |
| `16. Jhd.` | `1501` | `1600` | `1501-01-01/1600-12-31` |
| `1718-1722` | `1718` | `1722` | `1718-01-01/1722-12-31` |
| `1685-90` | `1685` | `1690` | `1685-01-01/1690-12-31` |
| `Mitte 18. Jhd.` | `1746` | `1755` | `1746-01-01/1755-12-31` |
| `1. Hälfte 18. Jhd.` | `1701` | `1750` | `1701-01-01/1750-12-31` |
| `14. Jahrhundert - 17. Jahrhundert` | `1301` | `1700` | `1301-01-01/1700-12-31` |
| `1685/1690` | `1685` | `1690` | `1685-01-01/1690-12-31` |
| `vor 1756` | `-inf` | `1755` | `..1755-12-31` |
| `nach 1679` | `1680` | `inf` | `1680-01-01..` |
| `letztes Viertel des 17. Jahrhunderts` | `1676` | `1700` | `1676-01-01/1700-12-31` |
| `Ende 17. Jhd.` | `1686` | `1700` | `1686-01-01/1700-12-31` |

Unparseable rows — and, under the default safe mode, compound entries that list
several distinct datings — yield `(None, None)` (or `None` for `iso-format`)
rather than raising, so a malformed entry never aborts a batch. Pass
`mode="aggressive"` to also collapse compound entries into one enclosing span.

### Automatic language detection

If `language` is omitted (or `None`), the language is detected from the input.

```python
unstruwwel(["19. Jahrhundert", "1. Hälfte 18. Jh."])  # detected: de
```

### Working with period objects

```python
from unstruwwel import Century

Century(15).take("last", type="third").time_span   # (1467, 1500)
Century(15).take(1, type="half").iso_format         # '1401-01-01/1450-12-31'
```

## Supported languages

English (`en`), German (`de`), French (`fr`), and Dutch (`nl`). Language data
lives in `src/unstruwwel/data/<code>.json`; adding a language is a matter of
adding another such file.

## Development

```bash
uv run pytest
```

## License

GPL-3.0-or-later. See [LICENSE.md](LICENSE.md).
