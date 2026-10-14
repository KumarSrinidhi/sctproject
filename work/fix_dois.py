import json, hashlib, collections

LOG = r'work\extraction_log.jsonl'
ROWS = r'work\rows_raw.jsonl'
CAND = r'work\candidates.json'

logs = [json.loads(l) for l in open(LOG, encoding='utf-8')]
h2doi = {}
for e in logs:
    d = e.get('doi')
    if d:
        h2doi[hashlib.md5(d.encode()).hexdigest()[:8]] = d

rows = [json.loads(l) for l in open(ROWS, encoding='utf-8')]
fixed = miss = 0
for r in rows:
    if not r.get('doi'):
        h = r['row_id'].split('-')[0]
        if h in h2doi:
            r['doi'] = h2doi[h]
            fixed += 1
        else:
            miss += 1
            print('NO DOI MAP for', r['row_id'], r.get('paper_title'))
print('doi fixed:', fixed, 'missing:', miss)

cand = json.load(open(CAND, encoding='utf-8'))
items = cand if isinstance(cand, list) else cand.get('candidates', [])
byd = {}
for c in items:
    d = (c.get('doi') or c.get('DOI') or '').lower()
    if d:
        byd[d] = c

t = 0
for r in rows:
    if not r.get('paper_title'):
        c = byd.get((r.get('doi') or '').lower())
        if c:
            r['paper_title'] = c.get('title') or c.get('paper_title') or ''
            r['source_url'] = r.get('source_url') or c.get('url') or f"https://doi.org/{r['doi']}"
            if c.get('year'):
                r['year'] = c['year']
            t += 1
print('titles patched:', t)

with open(ROWS, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

c = collections.Counter(r.get('doi', '') for r in rows)
print('rows with doi:', sum(n for d, n in c.items() if d), 'papers:', len([d for d in c if d]))
for d, n in sorted(c.items(), key=lambda x: -x[1]):
    print(n, d or '(empty)')
