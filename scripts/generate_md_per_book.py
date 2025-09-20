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
import re
from urllib.parse import quote
import text_processing


def sanitize_cell(s: str) -> str:
    if s is None:
        return ''
    return s.replace('\n', ' ').replace('|', '\\|').strip()


def fix_tractate_name(tractate: str, page: str) -> tuple[str, str]:
    """Fix tractate names that are concatenated with page markers.
    
    This handles multiple scenarios:
    1. Single word tractate + concatenated page: 'Avodah', 'Zarah29a:5' -> ('Avodah Zarah', '29a')
    2. Multi-word tractate split: 'Rosh', 'Hashanah11a:3' -> ('Rosh Hashanah', '11a')
    3. Normal cases: 'Berakhot', '2a' -> ('Berakhot', '2a')
    
    Returns tuple of (fixed_tractate, fixed_page)
    """
    # Check if page contains a tractate name concatenated with page marker
    # Pattern: LettersConcatenatedWithPageMarker like "Zarah29a:5", "Hashanah11a:3", "Batra22a"
    page_pattern = r'^([A-Za-z\s]+?)(\d+[ab])(?::\d+)?$'
    page_match = re.search(page_pattern, page)
    
    if page_match:
        # Page contains both tractate continuation and page number
        page_continuation = page_match.group(1).strip()
        actual_page = page_match.group(2)
        fixed_tractate = f"{tractate} {page_continuation}".strip()
        return fixed_tractate, actual_page
    
    # Check if tractate itself has concatenated page marker (backup case)
    tractate_pattern = r'^(.+?)(\d+[ab])(?::\d+)?$'
    tractate_match = re.search(tractate_pattern, tractate)
    
    if tractate_match:
        fixed_tractate = tractate_match.group(1).strip()
        # Keep original page if no concatenation found
        return fixed_tractate, page
    
    return tractate, page


def create_chavrutai_link(tractate: str, page: str, section: str) -> str:
    """Create a chavrutai.com hyperlink for Talmud locations.
    
    Examples:
    - tractate='Sanhedrin', page='90b', section='14' -> 
      '[Sanhedrin 90b:14](https://chavrutai.com/tractate/sanhedrin/90b#section-14)'
    - tractate='Rosh Hashanah', page='27b', section='4' ->
      '[Rosh Hashanah 27b:4](https://chavrutai.com/tractate/rosh%20hashanah/27b#section-4)'
    """
    # Create display text
    if section:
        display_text = f"{tractate} {page}:{section}"
    else:
        display_text = f"{tractate} {page}"
    
    # Create URL - tractate names should be lowercase and URL-encoded
    tractate_url = quote(tractate.lower())
    
    if section:
        url = f"https://chavrutai.com/tractate/{tractate_url}/{page}#section-{section}"
    else:
        url = f"https://chavrutai.com/tractate/{tractate_url}/{page}"
    
    return f"[{display_text}]({url})"


def main(infile: str, outdir: str):
    outdir_p = Path(outdir)
    outdir_p.mkdir(parents=True, exist_ok=True)

    with open(infile, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        books = {}
        for r in reader:
            book = r.get('book') or 'Unknown'
            chapter = int(r.get('chapter', 0)) if r.get('chapter', '').strip() else 0
            verse = int(r.get('verse', 0)) if r.get('verse', '').strip() else 0
            bible_loc = f"{book} {chapter}:{verse}" if book else ''
            verse_text = sanitize_cell(r.get('verse_text',''))
            
            raw_tractate = r.get('tractate', '')
            raw_page = r.get('page', '')
            tractate, page = fix_tractate_name(raw_tractate, raw_page)
            section = r.get('section') or ''
            
            # Create chavrutai hyperlink for Talmud location
            tal_loc = create_chavrutai_link(tractate, page, section)
            
            raw_full = r.get('full_text','')
            full_text = sanitize_cell(text_processing.process_full_text(raw_full))

            entry = {
                'chapter': chapter,
                'verse': verse,
                'bible_loc': bible_loc,
                'verse_text': verse_text,
                'tal_loc': tal_loc,
                'full_text': full_text
            }
            
            books.setdefault(book, []).append(entry)

    # Sort entries within each book by chapter and verse
    for book in books:
        books[book].sort(key=lambda x: (x['chapter'], x['verse']))

    for book, entries in books.items():
        safe_name = book.replace('/', '_').replace(' ', '_')
        out_file = outdir_p / f"{safe_name}.md"
        with out_file.open('w', encoding='utf-8') as fh:
            fh.write(f"# {book} — concordance\n\n")
            fh.write(f"This file was generated from `{infile}` and contains {len(entries)} entries.\n\n")
            
            # Group entries by chapter
            current_chapter = None
            for entry in entries:
                chapter = entry['chapter']
                
                # Start new chapter section if chapter changed
                if chapter != current_chapter:
                    if current_chapter is not None:
                        fh.write('\n')  # Add spacing between chapters
                    
                    current_chapter = chapter
                    fh.write(f"## Chapter {chapter}\n\n")
                    fh.write('| Bible Verse Location | Bible Verse Text | Talmud Location | Talmud Full text |\n')
                    fh.write('|---|---|---|---|\n')
                
                # Write the entry
                fh.write(f"| {entry['bible_loc']} | {entry['verse_text']} | {entry['tal_loc']} | {entry['full_text']} |\n")

    print('Wrote', len(books), 'book files to', outdir)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--infile', default='data/berakhot_concordance_export.csv')
    p.add_argument('-o', '--outdir', default='docs/books')
    args = p.parse_args()
    main(args.infile, args.outdir)
