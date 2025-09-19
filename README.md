# bible-rabbinic-index

This repository extracts Bible-verse citations from an English translation of the Talmud
and builds a concordance mapping Bible references -> Talmud sections where they are cited.

Current workflow
- Input: place the Talmud English CSV in the repository root (the file you uploaded is named:
	`Berakhot - en - William Davidson Edition - English.csv`). This file is ignored by git.
- Extraction: `scripts/extract_concordance_from_csv.py` — parses the CSV, uses BeautifulSoup to
	find bolded Bible quotations and parenthetical citations, canonicalizes book names, and
	writes `data/berakhot_concordance_csv.json` (normalized JSON output).
- Export: `scripts/export_concordance_csv.py` — deduplicates and sorts the concordance and writes
	`data/berakhot_concordance_export.csv` with columns:
	`book, chapter, verse, tractate, page, section, verse_text, full_text`.

Dependencies
- Python 3.8+ and the following pip packages:
	- beautifulsoup4

Quick start
1. Install dependencies (recommended inside a venv):

```bash
python3 -m pip install --user -r requirements.txt
```

2. Run the extractor (reads the CSV in repository root):

```bash
python3 scripts/extract_concordance_from_csv.py
```

3. Export deduplicated, sorted CSV:

```bash
python3 scripts/export_concordance_csv.py
```

Outputs
- `data/berakhot_concordance_csv.json` — JSON mapping normalized verse keys (e.g., "Genesis 1:5") to
	a list of entries containing: book, chapter, verse, tractate (Talmud tractate), page (daf), section,
	verse_text (the bolded text from the Talmud), and full_text (full HTML-ish section text).
- `data/berakhot_concordance_export.csv` — CSV export with columns matching the fields above.

Notes and next steps
- The extractor currently excludes parenthetical citations that begin with common prefixes like
	"see", "cf.", "compare" and similar.
- The book canonicalization is basic; if you want broader normalization (abbreviations, alt names),
	I can extend the mapping.

If you want me to add a lookup CLI, tests, or more robust canonicalization, tell me which and I'll add it.