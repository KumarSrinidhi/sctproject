# Phase 3A: thorough re-scan of previously "no absolute k" fulltexts
import re, os, json

FT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fulltext')

# unicode minus variants
MINUS = '[\u2212\u2013\u2014-]'
UNIT_PATTERNS = [
    r'W\s*[/\u2044]?\s*m(?:inus)?\s*' + MINUS + r'?\s*1?\s*[K\u00b7\u22c5\u2022⋅]?\s*',
    r'W\s*m' + MINUS + r'\s*1\s*K' + MINUS + r'\s*1',
    r'W\s*\(\s*m\s*[·⋅]\s*K\s*\)',
    r'W\s*m' + MINUS + r'1\s*K' + MINUS + r'1',
    r'W/(m[·⋅]?K)',
    r'W/m[·⋅]?K',
    r'W/cm[·⋅]?K',
    r'W\s*cm' + MINUS + r'\s*1\s*K' + MINUS + r'\s*1',
    r'mW/(m[·⋅]?K)',
    r'mW/m[·⋅]?K',
]

TARGETS = [
    '10.3390_polym11071156.txt',
    '10.3390_molecules21050670.txt',
    '10.3390_polym10030277.txt',
    '10.3390_nano9101396.txt',
    '10.1039_c8ra10645b.txt',
    '10.31248_ajps2025.124.txt',
]

# a numeric value possibly separated by whitespace/newline from unit
NUM = r'\d+(?:\.\d+)?'
# value before unit: "2.45 W/mK", "2.45 W m\u22121 K\u22121"
value_before = re.compile(
    r'(' + NUM + r')\s*(?:\u00b1\s*' + NUM + r')?\s*(' +
    '|'.join(UNIT_PATTERNS) + r')', re.IGNORECASE)
# unit before value: "W/mK of 2.45", "W m-1 K-1 was 2.45"
value_after = re.compile(
    r'(' + '|'.join(UNIT_PATTERNS) + r')\s*(?:of|was|were|is|=|:)?\s*(' + NUM + r')', re.IGNORECASE)

for fname in TARGETS:
    path = os.path.join(FT, fname)
    if not os.path.exists(path):
        print(f'=== {fname}: MISSING ===')
        continue
    text = open(path, encoding='utf-8', errors='replace').read()
    print(f'\n=== {fname} ({len(text)} chars) ===')
    hits = []
    for m in value_before.finditer(text):
        s, e = m.span()
        ctx = text[max(0, s-120):min(len(text), e+80)].replace('\n', ' | ')
        hits.append(('VALUE-BEFORE', m.group(1), m.group(2), ctx))
    for m in value_after.finditer(text):
        s, e = m.span()
        ctx = text[max(0, s-120):min(len(text), e+80)].replace('\n', ' | ')
        hits.append(('VALUE-AFTER', m.group(2), m.group(1), ctx))
    print(f'  total unit-value hits: {len(hits)}')
    for tag, val, unit, ctx in hits[:60]:
        print(f'  [{tag}] {val} || {unit!r}')
        print(f'    ...{ctx}...')
