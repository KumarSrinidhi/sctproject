import urllib.request, urllib.parse, json, os

def epmc(q, n=100):
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
        {'query': q, 'format': 'json', 'pageSize': n, 'resultType': 'core'})
    req = urllib.request.Request(url, headers={'User-Agent': 'research-tool/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

QUERIES = [
    'TITLE_ABS:"thermal conductivity" AND TITLE_ABS:epoxy AND TITLE_ABS:"boron nitride" AND OPEN_ACCESS:y AND PUB_YEAR:[2010 TO 2026]',
    'TITLE_ABS:"thermal conductivity" AND TITLE_ABS:epoxy AND (TITLE_ABS:AlN OR TITLE_ABS:"aluminum nitride") AND OPEN_ACCESS:y AND PUB_YEAR:[2010 TO 2026]',
    'TITLE_ABS:"thermal conductivity" AND TITLE_ABS:polymer AND TITLE_ABS:BN AND TITLE_ABS:composite AND OPEN_ACCESS:y AND PUB_YEAR:[2015 TO 2026]',
    'TITLE_ABS:"thermal conductivity" AND (TITLE_ABS:BNNS OR TITLE_ABS:"boron nitride nanosheet") AND OPEN_ACCESS:y',
]

known = set()
if os.path.exists(r'work\candidates.json'):
    cand = json.load(open(r'work\candidates.json', encoding='utf-8'))
    for c in (cand if isinstance(cand, list) else cand.get('candidates', [])):
        d = (c.get('doi') or '').lower()
        if d:
            known.add(d)
prev = {}
if os.path.exists(r'work\epmc_wave2.json'):
    for v in json.load(open(r'work\epmc_wave2.json')):
        prev[v['doi']] = v

seen = dict(prev)
for q in QUERIES:
    try:
        d = epmc(q, 100)
    except Exception as e:
        print('ERR', e)
        continue
    print('hits=', d['hitCount'], '|', q[:70])
    for r in d['resultList']['result']:
        doi = (r.get('doi') or '').lower()
        if doi and doi not in seen:
            seen[doi] = dict(doi=doi, title=r.get('title'), year=r.get('pubYear'),
                             pmcid=r.get('pmcid'), journal=r.get('journalTitle'),
                             oa=r.get('isOpenAccess'), in_candidates=doi in known)

new = [v for v in seen.values() if not v.get('in_candidates')]
json.dump(list(seen.values()), open(r'work\epmc_wave2.json', 'w', encoding='utf-8'), indent=1)
print('total unique', len(seen), '| not in wave1 candidates:', len(new))
for v in new:
    print(v['year'], v['doi'], '|', (v.get('journal') or '')[:28], '|', (v.get('title') or '')[:90])
