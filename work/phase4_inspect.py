import json, os, collections, csv

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(BASE, 'rows_raw.jsonl')

rows = [json.loads(l) for l in open(ROWS, encoding='utf-8') if l.strip()]
print('total rows:', len(rows))
print('unique row_ids:', len(set(r['row_id'] for r in rows)))

abs_rows = [r for r in rows if str(r.get('source_location','')).startswith('Abstract')]
print('abstract-prefixed rows:', len(abs_rows))
by_doi = collections.OrderedDict()
for r in abs_rows:
    by_doi.setdefault(r['doi'], []).append(r)
print('distinct DOIs:', len(by_doi))
for d, rs in by_doi.items():
    print(f"  {d}  n={len(rs)}  title={rs[0]['paper_title'][:60]!r}")
    for r in rs:
        print(f"     {r['row_id']}  k={r['k_composite_W_mK']}  load_vol={r['filler_loading_vol_pct']} load_wt={r['filler_loading_wt_pct']}  loc={r['source_location'][:70]!r}")

conf = collections.Counter(r['confidence'] for r in rows)
print('confidence:', dict(conf))
vs = collections.Counter(r['value_source'] for r in rows)
print('value_source:', dict(vs))

# figure rows
fig = [r for r in rows if r.get('value_source') == 'figure' or 'igure' in str(r.get('source_location',''))]
print('figure-ish rows:', len(fig))
for r in fig:
    print('   ', r['row_id'], r['doi'], r['source_location'][:60], r['confidence'])

# any local fulltext for the abstract DOIs
ft = set(os.listdir(os.path.join(BASE, 'fulltext')))
print('\nlocal fulltext availability for abstract DOIs:')
for d in by_doi:
    slug = d.replace('/', '_') + '.txt'
    print('  ', d, '->', 'YES' if slug in ft else 'no')

# check which local fulltexts are unused vs dataset
used_dois = set(r['doi'] for r in rows)
unused = [f for f in sorted(ft) if f.endswith('.txt') and f.replace('_','/').replace('.txt','') not in used_dois]
print('\nlocal fulltexts not represented in dataset:', len(unused))
for u in unused[:40]:
    print('   ', u)
