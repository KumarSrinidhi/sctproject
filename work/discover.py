import json, time, urllib.parse, urllib.request, os

QUERIES = [
    # Family 1: broad material combinations
    'epoxy boron nitride thermal conductivity composite',
    'epoxy resin aluminum nitride thermal conductivity composite',
    'epoxy h-BN effective thermal conductivity',
    'epoxy ceramic filler thermal transport experimental',
    # Family 2: morphology
    'boron nitride nanosheets epoxy thermal conductivity',
    'boron nitride platelets epoxy thermal conductivity',
    'spherical aluminum nitride epoxy thermal conductivity',
    'aligned boron nitride epoxy thermal conductivity',
    'boron nitride nanotube epoxy thermal conductivity',
    # Family 3: functionalization / interfaces
    'silane functionalized boron nitride epoxy thermal conductivity',
    'hydroxylated boron nitride epoxy thermal conductivity',
    'polydopamine boron nitride epoxy thermal conductivity',
    'surface modified aluminum nitride epoxy thermal conductivity',
    # Family 4: processing / structures
    'three dimensional boron nitride network epoxy thermal conductivity',
    'freeze cast boron nitride epoxy thermal conductivity',
    'vacuum assisted infiltration boron nitride epoxy thermal conductivity',
    'boron nitride aerogel epoxy thermal conductivity',
    # Family 5: measurement / numerical data
    'epoxy boron nitride laser flash thermal conductivity',
    'BN epoxy composite thermal conductivity volume fraction',
    'epoxy composite thermal conductivity experimental filler loading',
    'epoxy aluminum nitride hot disk thermal conductivity',
    # Optional matrices
    'silicone boron nitride thermal conductivity composite',
    'polyimide boron nitride thermal conductivity composite',
    'PDMS boron nitride thermal conductivity composite',
]

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'research-agent/1.0 (mailto:research@example.org)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

seen = {}
for q in QUERIES:
    params = urllib.parse.urlencode({
        'search': q,
        'filter': 'is_retracted:false,type:article',
        'per-page': '50',
        'select': 'id,doi,title,publication_year,primary_location,open_access,authorships,type,cited_by_count',
    })
    url = 'https://api.openalex.org/works?' + params
    try:
        data = fetch(url)
    except Exception as e:
        print('ERR', q, e)
        time.sleep(2)
        continue
    n = 0
    for w in data.get('results', []):
        title = (w.get('title') or '').lower()
        if not title:
            continue
        # scope filter on title (loose; screening happens later)
        if 'epoxy' not in title and 'silicone' not in title and 'polyimide' not in title and 'pdms' not in title and 'polydimethylsiloxane' not in title:
            continue
        if not any(k in title for k in ['thermal conduct', 'thermal transport', 'thermally conductive', 'heat conduct']):
            continue
        if not any(k in title for k in ['nitride', 'bn', 'aln', 'aluminum nitride', 'alumina', 'sic', 'silicon carbide', 'filler', 'composite', 'particle']):
            continue
        key = w.get('doi') or w.get('id')
        if key in seen:
            seen[key]['_matched_queries'].append(q)
            continue
        oa = w.get('open_access') or {}
        loc = w.get('primary_location') or {}
        src = (loc.get('source') or {})
        seen[key] = {
            'openalex_id': w.get('id'),
            'doi': w.get('doi'),
            'title': w.get('title'),
            'year': w.get('publication_year'),
            'journal': src.get('display_name'),
            'is_oa': oa.get('is_oa'),
            'oa_url': oa.get('oa_url'),
            'cited_by': w.get('cited_by_count'),
            '_matched_queries': [q],
        }
        n += 1
    print(f'{q!r}: +{n} (total {len(seen)})')
    time.sleep(0.35)

out = sorted(seen.values(), key=lambda x: (-(x['cited_by'] or 0)))
with open(os.path.join(os.path.dirname(__file__), 'candidates_openalex.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('TOTAL', len(out), '| OA:', sum(1 for x in out if x['is_oa']))
