# Project overview
----------------
This project constructs a comprehensive concordance mapping Bible verses to their citations in Talmudic literature. The system processes the complete Steinsaltz English translation of the Babylonian Talmud, extracting bolded biblical quotations and their parenthetical citations (e.g., "(Genesis 1:5)") to create detailed cross-reference tables.

The final output provides researchers with structured access to 17,000+ biblical citations across all Talmudic tractates, organized by biblical book with direct links to the Chavrutai online study platform. Rabbinic Index

Project overview
----------------
This project constructs a concordance mapping Bible verses to locations in the Talmud where those
verses are cited. The current implementation parses an English translation of a Talmud tractate and
extracts bolded quotations followed by parenthetical citations (e.g., “(Genesis 1:5)”).

Repository layout
-----------------
- `scripts/extract_concordance_from_csv.py` — extractor with robust parsing logic for multi-word tractate names, HTML processing of biblical quotations, and citation normalization
- `scripts/export_concordance_csv.py` — exporter that deduplicates entries and sorts by traditional biblical book order  
- `scripts/generate_md_per_book.py` — markdown generator with chapter organization, Chavrutai hyperlinks, and enhanced formatting
- `scripts/text_processing.py` — utilities for Hebrew text processing, HTML sanitization, and citation parsing
- `data/berakhot_concordance_csv_fixed.json` — complete normalized JSON concordance (19MB, ~80k entries)
- `data/berakhot_concordance_export_fixed.csv` — final deduplicated CSV export (17,138 entries)
- `docs/books/` — 38 per-book markdown files with organized concordance tables
- Input CSVs: Complete Steinsaltz Talmud data (not tracked in Git)

Key features
------------
- **Comprehensive coverage**: Processes complete Babylonian Talmud (80k+ source entries)
- **Multi-word tractate parsing**: Correctly handles "Rosh Hashanah", "Bava Batra", "Avodah Zarah", etc.
- **Chapter organization**: Markdown output grouped by biblical chapters with clear section headers
- **Chavrutai integration**: Direct hyperlinks to specific Talmudic passages with section anchors
- **Citation accuracy**: Robust HTML parsing excludes cross-references ("see", "cf.", "compare")
- **Canonical ordering**: Output follows traditional Jewish biblical book sequence
- **Rich metadata**: Preserves both display text and HTML source for debugging
- **Deduplication**: Intelligent removal of duplicate citations by verse-tractate combinations

Data processing pipeline
-----------------------
The system follows a three-stage workflow:

1. **Extract** (`extract_concordance_from_csv.py`) - Parses Talmudic HTML text, identifies biblical quotations, extracts citations, normalizes book names, and handles multi-word tractate names correctly

2. **Export** (`export_concordance_csv.py`) - Deduplicates by verse-tractate combinations, sorts by traditional biblical order, produces clean CSV output

3. **Generate** (`generate_md_per_book.py`) - Creates organized markdown files with chapter sections, Chavrutai hyperlinks, and researcher-friendly formatting

Each stage includes comprehensive error handling, logging, and data validation to ensure accuracy across the complete dataset.

Usage
-----
**Quick start for researchers:**
View the generated concordance tables in `docs/books/` - each biblical book has its own markdown file with organized citations and direct links to study materials.

**Processing new data:**

Install dependencies:
```bash
python3 -m pip install --user -r requirements.txt
```

Run complete processing pipeline:
```bash
# 1. Extract citations from source CSV
python3 scripts/extract_concordance_from_csv.py -i "Complete Steinsaltz CSV file" -o data/berakhot_concordance_csv_fixed.json

# 2. Export to deduplicated CSV  
python3 scripts/export_concordance_csv.py -i data/berakhot_concordance_csv_fixed.json -o data/berakhot_concordance_export_fixed.csv

# 3. Generate organized markdown files
python3 scripts/generate_md_per_book.py -i data/berakhot_concordance_export_fixed.csv -o docs/books
```

Technical specifications
-----------------------
- **Python 3.8+** required
- **Dependencies**: BeautifulSoup4 for HTML parsing (see `requirements.txt`)
- **Input format**: CSV with HTML-formatted Talmudic text columns
- **Output formats**: JSON (intermediate), CSV (data), Markdown (presentation)
- **Processing capacity**: Handles 80k+ entries, generates 17k+ unique citations
- **Memory usage**: ~19MB JSON files, efficient streaming processing

Data schema
-----------
Each concordance entry contains:
- `book`, `chapter`, `verse` - Biblical reference components  
- `tractate`, `page`, `section` - Talmudic location identifiers
- `verse_text` - Extracted biblical quotation (display)
- `verse_html` - Original HTML source (debugging)
- `full_text` - Complete Talmudic context passage

