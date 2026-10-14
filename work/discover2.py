import json, time, urllib.parse, urllib.request, os, sys

UA = 'research-agent/1.0 (mailto:research@example.org)'

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))

QUERIES = [
    'epoxy boron nitride thermal conductivity',
    'epoxy resin aluminum nitride thermal conductivity',
    'boron nitride nanosheets epoxy thermal conductivity',
    'boron nitride platelet epoxy thermal conductivity',
    'silane functionalized boron nitride epoxy thermal conductivity',
    'polydopamine boron nitride epoxy thermal conductivity',
    'three dimensional boron nitride network epoxy thermal conductivity',
    'aligned boron nitride epoxy thermal conductivity',
    'aluminum nitride epoxy composite thermal conductivity',
    'epoxy composite thermal conductivity filler loading',
    'thermally conductive epoxy composite boron nitride',
    'epoxy h-BN composite through-plane thermal conductivity',
    'silicone boron nitride thermal conductivity composite',
    'PDMS boron nitride thermal conductivity composite',
    'polyimide boron nitride thermal conductivity',
]

def relevant(title):
    t = title.lower()
    if not any(k in t for k in ['epoxy', 'silicone', 'polyimide', 'pdms', 'polydimethylsiloxane', 'resin']):
        return False
    if not any(k in t for k in ['thermal conduct', 'thermal transport', 'thermally conductive', 'heat conduct', 'thermoconduct']):
        return False
    if not any(k in t for k in ['nitride', 'bn', 'aln', 'alumina', 'aluminum oxide', 'sic', 'silicon carbide', 'silicon nitride', 'filler', 'composite', 'particle']):
        return False
    return True

candidates = {}

def add(key, rec):
    if key in candidates:
        candidates[key].update({k: v for k, v in rec.items() if v not in (None, [], '')})
    else:
        candidates[key] = rec

# ---- Crossref ----
for q in QUERIES:
    params = urllib.parse.urlencode({
        'query.bibliographic': q,
        'rows': '40',
        'select': 'DOI,title,published,container-title,link,license,type,URL,author',
        'filter': 'type:journal-article',
        'mailto': 'research@example.org',
    })
    try:
        d = fetch('https://api.crossref.org/works?' + params)
    except Exception as e:
        print('CROSSREF ERR', q, e); time.sleep(5); continue
    n = 0
    for it in d['message'].get('items', []):
        title = (it.get('title') or [''])[0]
        if not title or not relevant(title):
            continue
        doi = it.get('DOI')
        year = None
        try:
            year = (it['published']['date-parts'][0][0])
        except Exception:
            pass
        lic = [l.get('URL', '') for l in it.get('license', [])]
        links = [l.get('URL') for l in it.get('link', []) if l.get('URL')]
        add('crossref:' + doi, {
            'source': 'crossref', 'doi': doi, 'title': title, 'year': year,
            'journal': (it.get('container-title') or [''])[0], 'url': it.get('URL'),
            'license': lic, 'fulltext_links': links,
        })
        n += 1
    print(f'crossref {q!r}: +{n} (total {len(candidates)})')
    time.sleep(1.0)

# ---- Europe PMC ----
for q in QUERIES[:10]:
    params = urllib.parse.urlencode({
        'query': f'TITLE:"{q}" AND (OPEN_ACCESS:y OR SRC:PPR)',
        'format': 'json', 'pageSize': '40', 'resultType': 'core',
    })
    try:
        d = fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + params)
    except Exception as e:
        print('EPMC ERR', q, e); time.sleep(5); continue
    n = 0
    for it in d.get('resultList', {}).get('result', []):
        title = it.get('title') or ''
        if not title or not relevant(title):
            continue
        doi = it.get('doi')
        key = 'epmc:' + (doi or it.get('id'))
        add(key, {
            'source': 'europepmc', 'doi': doi, 'title': title.rstrip('.'), 'year': int(it.get('pubYear') or 0) or None,
            'journal': it.get('journalTitle'), 'pmcid': it.get('pmcid'),
            'epmc_id': it.get('id'), 'is_oa': it.get('isOpenAccess') == 'Y',
            'fulltext_links': [f"https://www.ebi.ac.uk/europepmc/webservices/rest/{it['pmcid']}/fullTextXML"] if it.get('pmcid') else [],
        })
        n += 1
    print(f'epmc {q!r}: +{n} (total {len(candidates)})')
    time.sleep(1.0)

# ---- Semantic Scholar ----
for q in QUERIES[:8]:
    params = urllib.parse.urlencode({
        'query': q, 'limit': '40',
        'fields': 'title,year,externalIds,openAccessPdf,journal,venue',
    })
    try:
        d = fetch('https://api.semanticscholar.org/graph/v1/paper/search?' + params)
    except Exception as e:
        print('S2 ERR', q, str(e)[:80]); time.sleep(8); continue
    n = 0
    for it in d.get('data', []):
        title = it.get('title') or ''
        if not title or not relevant(title):
            continue
        doi = (it.get('externalIds') or {}).get('DOI')
        oa = it.get('openAccessPdf') or {}
        key = 's2:' + (doi or it.get('paperId'))
        add(key, {
            'source': 'semantic_scholar', 'doi': doi, 'title': title, 'year': it.get('year'),
            'journal': (it.get('journal') or {}).get('name') or it.get('venue'),
            'oa_pdf': oa.get('url'), 's2_id': it.get('paperId'),
        })
        n += 1
    print(f's2 {q!r}: +{n} (total {len(candidates)})')
    time.sleep(4.0)

out = sorted(candidates.values(), key=lambda x: (x.get('year') or 0), reverse=True)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'candidates.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('TOTAL', len(out))
