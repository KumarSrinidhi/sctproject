import json, os, re, time, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
S2 = 'https://api.semanticscholar.org/graph/v1/paper/DOI:%s?fields=title,abstract,year,venue,isOpenAccess,openAccessPdf,externalIds'

rows = [json.loads(l) for l in open(os.path.join(BASE, 'rows_raw.jsonl'), encoding='utf-8')]
have = {r['doi'].lower() for r in rows}
cands = json.load(open(os.path.join(BASE, 'candidates.json'), encoding='utf-8'))

K_PAT = re.compile(
    r'([\d]+\.?\d*)\s*(?:\u00b1\s*[\d.]+\s*)?'
    r'W\s*(?:/|\u00b7|/)?\s*\(?\s*m(?:\s*[\u2212\-]\s*1\s*K\s*[\u2212\-]\s*1|/\s*\u00b7?\s*K|K)?\)?'
    r'|([\d.]+)\s*(?:W|mK|Wm)', re.I)

SCOPE_OK = re.compile(r'epox|bisphenol|DGEBA|cyanate|bismaleimide|phenolic|polyimide|silicone|PEEK|PA-|nylon', re.I)
CERAMIC = re.compile(r'BN|boron nitride|AlN|aluminium nitride|aluminum nitride|alumina|Al2O3|Al\(_?2\)|SiC|silicon carbide|MgO|ZnO|Si3N4|nitride|ceramic|hybrid', re.I)
CARBON = re.compile(r'graphene|carbon nanotube|CNT|MWCNT|SWCNT|carbon fiber|graphite|carbon nanofiber', re.I)

out = []
seen = set()
for c in cands:
    d = (c.get('doi') or '').lower()
    if not d or d in have or d in seen:
        continue
    seen.add(d)
    try:
        req = urllib.request.Request(S2 % d, headers={'User-Agent': 'research-agent/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            rec = json.loads(r.read())
    except Exception as e:
        if '429' in str(e):
            time.sleep(20)
            try:
                req = urllib.request.Request(S2 % d, headers={'User-Agent': 'research-agent/1.0'})
                with urllib.request.urlopen(req, timeout=30) as r:
                    rec = json.loads(r.read())
            except Exception as e2:
                out.append(dict(doi=d, error=str(e2)[:80]))
                continue
        else:
            out.append(dict(doi=d, error=str(e)[:80]))
            continue
    ab = rec.get('abstract') or ''
    title = rec.get('title') or c.get('title') or ''
    if not ab:
        continue
    hits = []
    for m in K_PAT.finditer(ab):
        ctx = ab[max(0, m.start() - 90):m.end() + 90].replace('\n', ' ')
        hits.append(ctx)
    if hits and SCOPE_OK.search(title + ' ' + ab):
        cer = bool(CERAMIC.search(title + ' ' + ab))
        car = bool(CARBON.search(title + ' ' + ab))
        out.append(dict(doi=d, title=title, year=rec.get('year') or c.get('year'),
                        venue=rec.get('venue'), ceramic=cer, carbon=car,
                        oa_pdf=(rec.get('openAccessPdf') or {}).get('url'),
                        k_hits=hits[:8], abstract=ab[:4000]))
    time.sleep(1.2)

json.dump(out, open(os.path.join(BASE, 'phase3c_abstract_hits.json'), 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
n_hit = sum(1 for e in out if e.get('k_hits'))
print('abstracts with k-pattern:', n_hit, 'records:', len(out))
for e in out:
    if e.get('k_hits'):
        print('-', e['doi'], '| ceramic=', e.get('ceramic'), '| carbon=', e.get('carbon'),
              '|', (e.get('title') or '')[:80])
