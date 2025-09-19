import re

# Hebrew nikud ranges regex (from the TS file)
NIKUD_RE = re.compile(r"[\u0591-\u05AF\u05B0-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7]")


def remove_nikud(text: str) -> str:
    if not text:
        return ''
    return NIKUD_RE.sub('', text)


def split_hebrew_text(text: str) -> str:
    if not text:
        return ''
    processed = text
    # ?! as unit
    processed = re.sub(r'\?\!', '?!\n', processed)
    # handle ? not followed by !
    processed = re.sub(r'\?(?!\!)', '?\n', processed)
    # handle ! not preceded by ?
    processed = re.sub(r'(?<!\?)\!', '!\n', processed)
    # other punctuation
    marks = ['\.', ',', '–', ':', ';', '\\"\\s', ' - ', '\u05C3']
    for m in marks:
        try:
            processed = re.sub(m, lambda mo: mo.group(0) + '\n', processed)
        except re.error:
            # skip bad regex patterns
            continue

    # clean up
    processed = re.sub(r'\n\s*\n', '\n', processed)
    processed = processed.strip()
    processed = re.sub(r'\n\s+', '\n', processed)
    return processed


def style_hebrew_parentheses(text: str) -> str:
    if not text:
        return ''
    return re.sub(r'\(([^)]+)\)', r'<span class="biblical-quote">(\1)</span>', text)


def process_hebrew_text(text: str) -> str:
    if not text:
        return ''
    processed = remove_nikud(text)
    processed = split_hebrew_text(processed)
    processed = style_hebrew_parentheses(processed)
    # normalize whitespace while keeping paragraph breaks
    processed = re.sub(r'[ \t]+', ' ', processed)
    processed = re.sub(r'\n[ \t]+', '\n', processed)
    processed = re.sub(r'[ \t]+\n', '\n', processed)
    return processed.strip()


def generate_sexual_terms():
    base_terms = ["intercourse", "sexual intercourse", "sexual relations", "intimacy"]
    conjugations = [
        ("engage in", "have sex"),
        ("engages in", "has sex"),
        ("engaged in", "had sex"),
        ("engaging in", "having sex"),
        ("have", "have sex"),
        ("has", "has sex"),
        ("had", "had sex"),
        ("having", "having sex"),
    ]
    res = {}
    for prefix, replacement in conjugations:
        for term in base_terms:
            res[f"{prefix} {term}"] = replacement
    # standalone
    res.update({"sexual intercourse": "sex", "intercourse": "sex", "conjugal relations": "sex", "relations": "sex"})
    return res


def replace_terms(text: str) -> str:
    if not text:
        return ''
    basic = {
        "GEMARA": "Talmud",
        "Gemara": "Talmud",
        "Rabbi": "R'",
        "The Sages taught": "A baraita states",
        "Divine Voice": "bat kol",
        "Divine Presence": "Shekhina",
        "divine inspiration": "Holy Spirit",
        "Divine Spirit": "Holy Spirit",
        "the Lord": "YHWH",
        "leper": "metzora",
        "leprosy": "tzara'at",
        "phylacteries": "tefillin",
        "gentile": "non-Jew",
        "gentiles": "non-Jews",
        "ignoramus": "am ha'aretz",
        "maidservant": "female slave",
        "maidservants": "female slaves",
        "barrel": "jug",
        "barrels": "jugs",
        "the Holy One, Blessed be He, ": "God ",
        "The Holy One, Blessed be He, ": "God ",
        "the Holy One, Blessed be He": "God",
        "The Holy One, Blessed be He": "God",
        "the Merciful One": "God",
        "the Almighty": "God",
        "the Omnipresent": "God",
        "Master of the Universe": "God!",
        "Sages": "rabbis",
        "mishna": "Mishnah",
        "rainy season": "winter",
        ", son of R' ": " ben "
    }
    terms = {**basic, **generate_sexual_terms()}

    # ordinal replacements (small subset)
    compound_ord = {
        "twenty-first": "21st",
        "twenty first": "21st",
        "twenty-second": "22nd",
    }
    basic_ord = {
        "third": "3rd",
        "fourth": "4th",
        "fifth": "5th",
        "sixth": "6th",
        "seventh": "7th",
        "eighth": "8th",
        "ninth": "9th",
        "tenth": "10th",
    }

    processed = text
    # apply term replacements (word boundaries, case-insensitive)
    for orig, repl in {**terms}.items():
        try:
            regex = re.compile(rf"\b{re.escape(orig)}\b", flags=re.IGNORECASE)
            processed = regex.sub(repl, processed)
        except re.error:
            continue

    for orig, repl in compound_ord.items():
        processed = re.sub(rf"\b{re.escape(orig)}\b", repl, processed, flags=re.IGNORECASE)

    for orig, repl in basic_ord.items():
        processed = re.sub(rf"\b{re.escape(orig)}\b", repl, processed, flags=re.IGNORECASE)

    return processed


def split_english_text(text: str) -> str:
    if not text:
        return ''
    processed = text

    # Process bold/strong content commas/colons: simple approach - add newline after commas/colons inside tags
    def replace_bold(match):
        tag = match.group(1)
        content = match.group(2)
        if not re.search(r'[,:]', content):
            return match.group(0)
        content = re.sub(r'([,:])', r'\1\n', content)
        return f"<{tag}>{content}</{tag}>"

    processed = re.sub(r'<(b|strong)[^>]*>([\s\S]*?)</\1>', replace_bold, processed, flags=re.IGNORECASE)
    processed = re.sub(r'<(b|strong)[^>]*>([,:])</\1>', r'\2\n', processed, flags=re.IGNORECASE)

    # Protect HTML tags
    html_tags = []
    placeholders = []
    def tag_repl(m):
        placeholders.append(m.group(0))
        ph = f"__HTML_TAG_{len(placeholders)-1}__"
        return ph

    processed = re.sub(r'</?\w+(?:\s+[^>]*)?>', tag_repl, processed)

    # Split on periods (avoid splitting after lowercase letter)
    processed = re.sub(r'\.(?!\s*[a-z])', '.\n', processed)
    # undo some abbreviation breaks
    processed = processed.replace('i.e.\n', 'i.e.').replace('e.g.\n', 'e.g.').replace('etc.\n', 'etc.').replace('vs.\n', 'vs.').replace('cf.\n', 'cf.')

    # Question marks
    processed = re.sub(r'\?(?!(\"|\'"\'|\"))', '?\n', processed)
    # Semicolons
    processed = processed.replace(';', ';\n')

    # Clean up
    processed = re.sub(r'\n\s*\n', '\n', processed)
    processed = processed.strip()
    processed = re.sub(r'\n\s+', '\n', processed)

    # Restore HTML tags
    for i, ph in enumerate(placeholders):
        processed = processed.replace(f'__HTML_TAG_{i}__', ph)

    # Final cleanups for orphaned quotes
    processed = re.sub(r',\n\n["\']\s*\n', ',\n\n', processed)
    processed = re.sub(r'\n["\']\s*\n', '\n', processed)
    processed = re.sub(r'\n["\']\s*$', '', processed)

    return processed


def process_english_text(text: str) -> str:
    if not text:
        return ''
    processed = replace_terms(text)
    processed = split_english_text(processed)
    processed = processed.replace('\r\n', '\n')
    processed = re.sub(r'\n{3,}', '\n\n', processed)
    processed = re.sub(r'[ \t]+', ' ', processed)
    processed = re.sub(r'\n[ \t]+', '\n', processed)
    processed = re.sub(r'[ \t]+\n', '\n', processed)
    return processed.strip()


def contains_hebrew(text: str) -> bool:
    return bool(re.search(r'[\u0590-\u05FF]', text))


def process_full_text(text: str) -> str:
    if not text:
        return ''
    # If contains Hebrew letters, use Hebrew processor, otherwise English
    if contains_hebrew(text):
        return process_hebrew_text(text)
    return process_english_text(text)
