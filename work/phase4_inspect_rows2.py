import json, os, collections
BASE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(BASE, 'rows_raw.jsonl'), encoding='utf-8')]
med = [r for r in rows if r.get('confidence') == 'Medium']
print('medium rows:', len(med))
print('medium abstract-prefixed:', sum(1 for r in med if str(r.get('source_location','')).startswith('Abstract')))
print('medium doi count:', len(set(r.get('doi') for r in med)))
bydoi = collections.defaultdict(list)
for r in med:
    bydoi[r.get('doi')].append(r)
for d, v in sorted(bydoi.items(), key=lambda x: -len(x[1])):
    print(d, len(v), '| value_source:', set(x.get('value_source') for x in v), '| sl:', v[0].get('source_location')[:60])
# value_source distribution
print('\nvalue_source:', dict(collections.Counter(r.get('value_source') for r in rows)))
# figure DOIs of interest
for target in ('10.3390/polym11071156', '10.3390/molecules21050670'):
    hits = [r for r in rows if r.get('doi') == target]
    print(f'\n{target}: {len(hits)} rows')
    for r in hits:
        print(' ', r.get('row_id'), r.get('k_composite_W_mK'), r.get('value_source'), r.get('confidence'), '|', r.get('source_location')[:70])
# row_id prefixes
pref = collections.Counter(r['row_id'].split('-')[0] for r in rows)
print('\nrow_id prefixes:', dict(pref))
# ETL-70 spot check
for r in rows:
    if r['row_id'].startswith('ETL-70'):
        print('ETL-70:', r.get('k_composite_W_mK'), r.get('doi'))
# dropped ids
dropped = ['ETL-70','ETL-105','ETL-115','ETL-127','ETL-157','ETL-180','ETL-213','ETL-16','ETL-24','ETL-33','ETL-42','ETL-49','ETL-61','ETL-89','ETL-99']
ids = set(r['row_id'] for r in rows)
print('dropped present:', [d for d in dropped if d in ids])
# unique ids
print('unique row_ids:', len(ids), 'of', len(rows))
