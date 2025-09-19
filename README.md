# Bible Rabbinic Index

Project overview
----------------
This project constructs a concordance mapping Bible verses to locations in the Talmud where those
verses are cited. The current implementation parses an English translation of a Talmud tractate and
extracts bolded quotations followed by parenthetical citations (e.g., “(Genesis 1:5)”).

Repository layout
-----------------
- `scripts/extract_concordance_from_csv.py` — extractor that parses the input CSV, uses an HTML
	parser to identify bolded quotations and nearby parenthetical citations, canonicalizes book names,
	and writes the normalized JSON output.
- `scripts/export_concordance_csv.py` — exporter that deduplicates, sorts, and serializes the
	concordance to CSV.
- `data/berakhot_concordance_csv.json` — normalized JSON concordance produced by the extractor.
- `data/berakhot_concordance_export.csv` — deduplicated, sorted CSV export produced by the exporter.
- `Berakhot - en - William Davidson Edition - English.csv` — input CSV (not tracked in Git).

Key behaviors
-------------
- Bold-detection: the extractor locates `<b>`/`<strong>` elements and considers adjacent text for
	parenthetical citations.
- Exclusions: parenthetical citations beginning with prefixes such as `see`, `cf.`, or `compare`
	are excluded from the concordance to avoid cross-references.
- Normalization: basic canonicalization of book names is applied (e.g., `I Samuel` → `1 Samuel`).
- Output schema: each concordance entry contains the fields: `book`, `chapter`, `verse`, `tractate`,
		`page`, `section`, `verse_text`, and `full_text`.

Recent notes
------------
- The per-book Markdown files in `docs/books/` now contain Bible-only outputs (non-biblical tractates
	such as Mishnah/Tosefta were removed). A backup of the earlier full set was kept briefly as
	`docs/books_bible_only/` but has since been removed and the Bible-only set is now the canonical
	`docs/books/` folder.
- The extractor now normalizes and unescapes extracted verse text and stores a `verse_html` field in
	the JSON for debugging. The exporter collapses whitespace and uses CSV quoting to avoid multiline
	CSV cells.

Regenerating per-book Markdown
-----------------------------
1. Run the extractor on your CSV to produce the normalized JSON (there is a `--infile`/`--outjson`
	 flag on the script):

```bash
python3 scripts/extract_concordance_from_csv.py -i "path/to/input.csv" -o data/berakhot_concordance_csv.json
```

2. Export to CSV:

```bash
python3 scripts/export_concordance_csv.py -i data/berakhot_concordance_csv.json -o data/berakhot_concordance_export.csv
```

3. Generate per-book Markdown (the generator accepts `-i` and `-o`):

```bash
python3 scripts/generate_md_per_book.py -i data/berakhot_concordance_export.csv -o docs/books
```

If you want Bible-only output, run the extractor as above — it now filters to canonical Biblical
book names by default. To change this behavior we can add a CLI flag; ask me if you want that.

Requirements
------------
- Python 3.8 or later
- Dependencies listed in `requirements.txt` (e.g., `beautifulsoup4`)

Usage
-----
Install dependencies (recommended within an isolated environment):

```bash
python3 -m pip install --user -r requirements.txt
```

Run the extractor (reads the CSV in the repository root):

```bash
python3 scripts/extract_concordance_from_csv.py
```

Produce the deduplicated CSV export:

```bash
python3 scripts/export_concordance_csv.py
```

