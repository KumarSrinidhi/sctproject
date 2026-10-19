import json, os, collections
BASE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(BASE, 'rows_raw.jsonl'), encoding='utf-8')]
print('n rows:', len(rows))
print('cols:', sorted(rows[0].keys()))
abst = [r for r in rows if str(r.get('source_location','')).startswith('Abstract')]
print('abstract-prefixed:', len(abst))
print('confidence:', dict(collections.Counter(r.get('confidence') for r in rows)))
bydoi = collections.defaultdict(list)
for r in abst:
    bydoi[r.get('doi')].append(r)
print('abstract dois:', len(bydoi))
for d, v in sorted(bydoi.items(), key=lambda x: -len(x[1]))[:30]:
    print(d, len(v), '| sample row_id:', v[0].get('row_id'), '| k:', [x.get('k_value') for x in v][:5])
fig = [r for r in rows if r.get('value_source') == 'figure']
print('\nfigure rows:', len(fig))
for r in fig:
    print(' ', r.get('row_id'), r.get('doi'), '|', r.get('source_location'), '| k=', r.get('k_value'), '|', r.get('confidence'))
