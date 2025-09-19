"""Generate one markdown file per biblical book from the exporter CSV.

Output files: docs/<Book>.md

Columns in each markdown table:
- Bible Verse Location | Bible Verse Text | Talmud Location | Talmud Full text

Usage:
  python3 scripts/generate_md_per_book.py -i data/berakhot_concordance_export.csv -o docs/
"""
import argparse
import csv
from pathlib import Path
import text_processing


def sanitize_cell(s: str) -> str:
    if s is None:
        return ''
    return s.replace('\n', ' ').replace('|', '\\|').strip()


def main(infile: str, outdir: str):
    outdir_p = Path(outdir)
    outdir_p.mkdir(parents=True, exist_ok=True)

    with open(infile, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        books = {}
        for r in reader:
            book = r.get('book') or 'Unknown'
            chapter = r.get('chapter') or ''
            verse = r.get('verse') or ''
            bible_loc = f"{book} {chapter}:{verse}" if book else ''
            verse_text = sanitize_cell(r.get('verse_text',''))
            tractate = r.get('tractate') or ''
            page = r.get('page') or ''
            section = r.get('section') or ''
            tal_loc = f"{tractate} {page}:{section}" if section else f"{tractate} {page}"
            raw_full = r.get('full_text','')
            full_text = sanitize_cell(text_processing.process_full_text(raw_full))

            entry = (bible_loc, verse_text, tal_loc, full_text)
            books.setdefault(book, []).append(entry)

    for book, entries in books.items():
        safe_name = book.replace('/', '_').replace(' ', '_')
        out_file = outdir_p / f"{safe_name}.md"
        with out_file.open('w', encoding='utf-8') as fh:
            fh.write(f"# {book} — concordance\n\n")
            fh.write(f"This file was generated from `{infile}` and contains {len(entries)} entries.\n\n")
            fh.write('| Bible Verse Location | Bible Verse Text | Talmud Location | Talmud Full text |\n')
            fh.write('|---|---|---|---|\n')
            for bible_loc, verse_text, tal_loc, full_text in entries:
                fh.write(f"| {bible_loc} | {verse_text} | {tal_loc} | {full_text} |\n")

    print('Wrote', len(books), 'book files to', outdir)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--infile', default='data/berakhot_concordance_export.csv')
    p.add_argument('-o', '--outdir', default='docs/books')
    args = p.parse_args()
    main(args.infile, args.outdir)
