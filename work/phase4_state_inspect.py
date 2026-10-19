import json, os, collections, re

BASE = r'work'
rows = [json.loads(l) for l in open(os.path.join(BASE,'rows_raw.jsonl'), encoding='utf-8')]
print('rows:', len(rows), 'papers:', len({r['doi'] for r in rows}))
conf = collections.Counter(r['confidence'] for r in rows)
print('confidence:', dict(conf))

# abstract-prefixed Medium rows
abs_med = [r for r in rows if r['confidence']!='High' and str(r['source_location']).lower().startswith('abstract')]
print('abstract-Medium rows:', len(abs_med), 'papers:', len({r['doi'] for r in abs_med}))
other_med = [r for r in rows if r['confidence']!='High' and not str(r['source_location']).lower().startswith('abstract')]
print('other-Medium rows:', len(other_med))
for r in other_med:
    print('  OTHER-MED:', r['row_id'], r['doi'], '|', r['source_location'][:80], '|', r['notes'][:100])

by_doi = collections.Counter(r['doi'] for r in abs_med)
for doi, n in sorted(by_doi.items(), key=lambda x:-x[1]):
    slug = doi.replace('/','_')
    ft = os.path.join(BASE,'fulltext', slug+'.txt')
    have = os.path.exists(ft) and os.path.getsize(ft)>2000
    print(f'  {doi} n={n} fulltext_local={have}')

# spot checks
for rid in ('ETL-70',):
    for r in rows:
        if r['row_id']==rid:
            print('spot', rid, 'wt:', r['filler_loading_wt_pct'], 'k:', r['k_composite_W_mK'])

p2 = json.load(open(os.path.join(BASE,'phase2_applied_changes.json'), encoding='utf-8'))
print('phase2 keys:', list(p2.keys())[:10])
# dropped ids
dropped = []
def find_dropped(obj):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if 'drop' in k.lower() and isinstance(v, list):
                dropped.extend(v)
            else:
                find_dropped(v)
    elif isinstance(obj, list):
        for v in obj: find_dropped(v)
find_dropped(p2)
print('dropped candidates sample:', dropped[:20])
