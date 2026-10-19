import json, os, collections

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(BASE, 'rows_raw.jsonl')
rows = [json.loads(l) for l in open(ROWS, encoding='utf-8') if l.strip()]

med = [r for r in rows if r['confidence'] == 'Medium']
print('Medium rows:', len(med))
by = collections.OrderedDict()
for r in med:
    by.setdefault(r['doi'], []).append(r)
print('Medium DOIs:', len(by))
for d, rs in by.items():
    print(f"{d} | n={len(rs)} | " + "; ".join(f"{r['row_id']} k={r['k_composite_W_mK']} {r['source_location'][:50]!r}" for r in rs))

# abstract-prefixed AND High (i.e. abstract+text with local fulltext)
ah = [r for r in rows if str(r.get('source_location','')).startswith('Abstract') and r['confidence']=='High']
print('\nabstract-prefixed but High:', len(ah))
# Medium not abstract-prefixed
mn = [r for r in med if not str(r.get('source_location','')).startswith('Abstract')]
print('Medium not abstract-prefixed:', len(mn))
for r in mn:
    print('   ', r['row_id'], r['doi'], repr(r['source_location'][:80]))
