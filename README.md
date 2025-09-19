# bible-rabbinic-index

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

Notes
-----
- The input CSV is ignored by Git and should be supplied outside the repository when working in a
	shared environment.
- The canonicalization step is minimal; expanding the canonical book-name mapping is recommended
	for larger-scale processing.

Contact and contributions
-------------------------
Contributions are welcome. For major changes (new features, normalization rules, or different data
sources), open a pull request with tests and a short description of the intended behavior.