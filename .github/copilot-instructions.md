# Bible Rabbinic Index - AI Coding Agent Instructions

## Project Overview
This project extracts Bible verse citations from Talmudic texts and creates a comprehensive concordance mapping Bible verses to their locations in rabbinic literature. The core workflow parses HTML-formatted CSV files, identifies bold quotations followed by parenthetical citations (e.g., "(Genesis 1:5)"), and generates structured outputs.

## Architecture & Data Flow
The system follows a three-stage pipeline:

1. **Extract** (`extract_concordance_from_csv.py`) - Parses input CSV, uses BeautifulSoup to find `<b>` tags, extracts parenthetical citations, canonicalizes book names via `BOOK_CANONICAL` dictionary, filters to `BIBLE_BOOKS` whitelist
2. **Export** (`export_concordance_csv.py`) - Deduplicates entries by (verse, section) tuple, sorts by traditional biblical book order via `BOOK_ORDER`, outputs CSV
3. **Generate** (`generate_md_per_book.py`) - Creates per-book markdown files with concordance tables, applies text processing via `text_processing.py`

### Key Data Structures
- **JSON Schema**: `{book, chapter, verse, tractate, page, section, verse_text, verse_html, full_text}`
- **CSV Output**: Deduplicated rows sorted by biblical order
- **Markdown Tables**: Bible Verse Location | Bible Verse Text | Talmud Location | Talmud Full text

## Critical Patterns & Conventions

### Text Processing Pipeline
- **HTML Parsing**: BeautifulSoup extracts bold text and adjacent parenthetical citations
- **Exclusion Logic**: Citations starting with "see", "cf.", "compare" are filtered out as cross-references
- **Book Canonicalization**: Roman numerals (I Samuel → 1 Samuel) via regex patterns
- **Hebrew Text Processing**: `text_processing.py` handles nikud removal, punctuation splitting, HTML escaping

### File Organization
- **Input**: Raw CSV files (not tracked in git) - `*William Davidson Edition*.csv`
- **Intermediate**: `data/berakhot_concordance_csv.json` - normalized JSON
- **Output**: `data/berakhot_concordance_export.csv` - deduplicated CSV
- **Documentation**: `docs/books/*.md` - per-book concordance tables

### Command Line Interface
All scripts support `-i/--infile` and `-o/--outfile` parameters. Default paths are defined as module constants (e.g., `IN = 'data/berakhot_concordance_csv.json'`).

## Essential Development Workflows

### Standard Processing Pipeline
```bash
# 1. Extract from CSV (produces JSON)
python3 scripts/extract_concordance_from_csv.py -i "input.csv" -o data/berakhot_concordance_csv.json

# 2. Export to deduplicated CSV
python3 scripts/export_concordance_csv.py -i data/berakhot_concordance_csv.json -o data/berakhot_concordance_export.csv

# 3. Generate per-book markdown
python3 scripts/generate_md_per_book.py -i data/berakhot_concordance_export.csv -o docs/books
```

### Dependencies & Environment
- **Python 3.8+** required
- **beautifulsoup4** only external dependency (see `requirements.txt`)
- Install: `python3 -m pip install --user -r requirements.txt`

## Project-Specific Implementation Details

### Book Name Normalization
The `BOOK_CANONICAL` dictionary handles common variants. Roman numerals are normalized via regex: `r'^(?P<roman>I|II|III|IV|V)\s+(?P<rest>.+)$'`. New book variants should be added to this dictionary, not handled ad-hoc.

### Citation Detection Logic
Bold text detection looks for `<b>` or `<strong>` tags followed by parenthetical citations within the same text block. The extractor specifically excludes meta-references (citations prefixed with "see", "cf.", "compare") to avoid cross-reference pollution.

### Output Deduplication
The exporter deduplicates by `(book, chapter, verse, tractate, page, section)` tuple, keeping one `full_text` per unique combination. Sort order follows `BOOK_ORDER` list using traditional biblical sequence.

### Text Sanitization
Markdown generation uses `sanitize_cell()` to escape pipe characters (`|` → `\\|`) and collapse newlines to prevent table formatting issues. Hebrew text processing includes nikud removal and punctuation-based paragraph splitting.

## Integration Points
- **Third-party**: TypeScript version of text processing utilities in `third_party/text-processing.ts` (reference implementation)
- **Data Schema**: JSON structure must maintain `verse_html` field for debugging alongside `verse_text` for display
- **Documentation**: `docs/BOOKS_INDEX.md` maintains traditional Jewish canonical order (Torah, Nevi'im, Ketuvim)

When extending functionality, preserve the three-stage pipeline architecture and maintain backward compatibility with existing JSON schema.