"""Extract verse -> full talmud section mappings from the uploaded CSV.

CSV format expected: two columns per row: reference (e.g., 'Berakhot 2a:1') and HTML-like text.
This script will group rows by daf (e.g., 'Berakhot 2a') and aggregate the full section text for that daf,
then scan for <b>...</b> spans followed by parenthetical citations like (Book 6:7).

Output: data/berakhot_concordance_csv.json mapping normalized verse keys to list of entries with daf and full text.
"""
import argparse
import csv
import json
import re
from collections import defaultdict
from html import unescape

from bs4 import BeautifulSoup


BOOK_CANONICAL = {
    # common English variants -> canonical name
    'I Samuel': '1 Samuel',
    'II Samuel': '2 Samuel',
    'I Kings': '1 Kings',
    'II Kings': '2 Kings',
    'I Chronicles': '1 Chronicles',
    'II Chronicles': '2 Chronicles',
    'I Samuel.': '1 Samuel',
    'II Samuel.': '2 Samuel',
}


def canonicalize_book(name: str) -> str:
    name = name.strip()
    # simple replacements
    if name in BOOK_CANONICAL:
        return BOOK_CANONICAL[name]
    # normalize roman numerals like 'I Samuel' -> '1 Samuel'
    m = re.match(r'^(?P<roman>I|II|III|IV|V)\s+(?P<rest>.+)$', name)
    if m:
        roman = m.group('roman')
        rest = m.group('rest')
        roman_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5'}
        return f"{roman_map.get(roman, roman)} {rest}"
    return name


def parse_ref(ref: str):
    # Expecting something like: 'Berakhot 2a:8' or 'Berakhot 2a:1-2' or 'Berakhot 2a'
    parts = ref.split()
    if not parts:
        return None
    book = parts[0]
    rest = "".join(parts[1:])
    # naive parse for daf:segment
    m = re.match(r'(?P<daf>\d+[ab])[:.]?(?P<seg>\d+)?', rest)
    if not m:
        daf = rest
        seg = ""
    else:
        daf = m.group('daf')
        seg = m.group('seg') or ""
    section_id = f"{book}.{daf}.{seg}" if seg else f"{book}.{daf}"
    return {"book": book, "daf": daf, "seg": seg, "section_id": section_id}


def extract_from_html(html_text: str):
    """Return list of tuples (verse_text, citation_book, chapter, verse) found in the html_text

    Uses BeautifulSoup to find bold (<b> or <strong>) tags and then searches for the first parenthetical
    citation following the tag. Excludes citations that start with 'see', 'cf', 'compare', 'vid' (case-insensitive).
    Also returns the exact text of the bold span as the verse_text.
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    results = []
    EXCLUDE_PREFIXES = ('see', 'cf', 'cf.', 'compare', 'vid', 'vid.')
    # find bold or strong tags
    for b in soup.find_all(['b', 'strong']):
        # raw text from the bold tag
        bold_text = b.get_text(separator=' ', strip=True)
        # normalize verse_text: unescape entities, collapse whitespace, trim
        verse_text = unescape(bold_text)
        verse_text = re.sub(r"\s+", " ", verse_text).strip()
        # keep raw HTML of the bold span for debugging
        verse_html = str(b)

        # look for the citation in the text that follows this tag
        tail = ''
        # gather following siblings text up to a certain length but stop if we hit another bold/strong
        for sib in b.next_siblings:
            # if we encounter another bold/strong tag, stop — we want the bold nearest the citation
            if hasattr(sib, 'name') and sib.name in ('b', 'strong'):
                break
            if hasattr(sib, 'get_text'):
                tail_piece = sib.get_text(separator=' ', strip=True)
            else:
                tail_piece = str(sib)
            tail += ' ' + tail_piece
            if len(tail) > 300:
                break
        # find parenthetical citations like (Deuteronomy 6:7)
        m = re.search(r'\((?P<book>[A-Za-z0-9\s\.\'"-]+?)\s+(?P<ch>\d+):(?P<vt>\d+)\)', tail)
        if m:
            book = m.group('book').strip()
            bl = book.lower()
            if any(bl.startswith(p) for p in EXCLUDE_PREFIXES):
                # skip entries like (see Isaiah 13:21) or (cf. Isaiah 13:21)
                continue
            book = canonicalize_book(book)
            results.append((verse_text, verse_html, book, int(m.group('ch')), int(m.group('vt'))))
    return results


def main(infile: str, outjson: str):
    """Process infile CSV and write normalized concordance to outjson."""
    concordance = defaultdict(list)

    with open(infile, newline='') as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            if i == 0:
                # header
                continue
            if len(row) < 2:
                continue
            ref = row[0].strip()
            text = unescape(row[1])
            parsed = parse_ref(ref)
            if not parsed:
                continue
            section = parsed['section_id']
            hits = extract_from_html(text)
            for verse_text, verse_html, book, ch, vt in hits:
                verse_key = f"{book} {ch}:{vt}"
                tractate = parsed['book']
                daf = parsed['daf']
                seg = parsed['seg']
                concordance[verse_key].append({
                    'book': book,
                    'chapter': ch,
                    'verse': vt,
                    'tractate': tractate,
                    'page': daf,
                    'section': seg,
                    'verse_text': verse_text,
                    'verse_html': verse_html,
                    'full_text': text
                })

    # write out normalized concordance
    with open(outjson, 'w', encoding='utf-8') as outfh:
        json.dump(concordance, outfh, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Extract concordance from CSV')
    p.add_argument('-i', '--infile', default='Berakhot - en - William Davidson Edition - English.csv',
                   help='Input CSV file (reference, html_text)')
    p.add_argument('-o', '--outjson', default='data/berakhot_concordance_csv.json',
                   help='Output JSON concordance file')
    args = p.parse_args()
    main(args.infile, args.outjson)
