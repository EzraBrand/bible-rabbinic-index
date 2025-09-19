"""Export concordance JSON to CSV with columns: verse, section, full_text

This exporter deduplicates by (verse, section) and sorts rows according to a
traditional book ordering and numeric chapter/verse.
"""
import argparse
import json
import csv
import re

IN = 'data/berakhot_concordance_csv.json'
OUT = 'data/berakhot_concordance_export.csv'

# A simple traditional book order for sorting. Extend if needed.
BOOK_ORDER = [
    'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
    'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings',
    '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther',
    'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon',
    'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel',
    'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi'
]

BOOK_INDEX = {b: i for i, b in enumerate(BOOK_ORDER)}


def parse_verse_key(verse_key: str):
    """Parse a verse key like 'Genesis 1:5' into (book, chapter, verse).

    If parsing fails, return (verse_key, 0, 0) so it sorts at the end.
    """
    m = re.match(r'^(?P<book>.+?)\s+(?P<ch>\d+):(?P<vt>\d+)$', verse_key)
    if not m:
        return (verse_key, 0, 0)
    book = m.group('book')
    ch = int(m.group('ch'))
    vt = int(m.group('vt'))
    # normalize roman numerals in book e.g., I Samuel -> 1 Samuel
    book = re.sub(r'^I\s+', '1 ', book)
    book = re.sub(r'^II\s+', '2 ', book)
    return (book, ch, vt)


def main(infile: str, outfile: str):
    with open(infile, encoding='utf-8') as f:
        data = json.load(f)

    # Deduplicate by (book,chapter,verse,tractate,page,section) and keep one full text per pair
    seen = set()
    rows = []
    for verse, entries in data.items():
        for e in entries:
            book = e.get('book', '')
            chapter = e.get('chapter', 0)
            verse_no = e.get('verse', 0)
            tractate = e.get('tractate', '')
            page = e.get('page', '')
            section = e.get('section', '')
            verse_text = e.get('verse_text', '')
            full_text = e.get('full_text', '')
            key = (book, chapter, verse_no, tractate, page, section)
            if key in seen:
                continue
            seen.add(key)
            rows.append((book, chapter, verse_no, tractate, page, section, verse_text, full_text))


    def sort_key(row):
        book, ch, vt, tractate, page, section, _, _ = row
        book_idx = BOOK_INDEX.get(book, 9999)
        return (book_idx, book, ch, vt, tractate, page, section)


    rows.sort(key=sort_key)

    with open(outfile, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(['book', 'chapter', 'verse', 'tractate', 'page', 'section', 'verse_text', 'full_text'])
        for r in rows:
            # sanitize fields to avoid multiline CSV cells
            sanitized = list(r)
            # replace newlines in full_text and verse_text
            if len(sanitized) >= 8:
                sanitized[6] = re.sub(r"\s+", " ", str(sanitized[6])).strip()
                sanitized[7] = re.sub(r"\s+", " ", str(sanitized[7])).strip()
            w.writerow(sanitized)

    print('Wrote', outfile, 'rows=', len(rows))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Export concordance JSON to CSV')
    p.add_argument('-i', '--infile', default=IN, help='Input JSON file')
    p.add_argument('-o', '--outfile', default=OUT, help='Output CSV file')
    args = p.parse_args()
    main(args.infile, args.outfile)
