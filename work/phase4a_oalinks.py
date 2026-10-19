import json, os, re, time, ssl, urllib.request, urllib.parse, warnings
warnings.filterwarnings('ignore')
BASE = r'work'
PDFS = os.path.join(BASE, 'phase4_pdfs'); os.makedirs(PDFS, exist_ok=True)
LOGP = os.path.join(BASE, 'phase4_oa_log.json')

TARGETS = [
 '10.1039/d4dt00979g','10.1002/slct.202507155','10.1016/j.compscitech.2020.108304',
 '10.1016/j.compscitech.2020.108322','10.1002/pc.27985','10.1016/j.jcomc.2020.100087',
 '10.1002/pc.29136','10.1088/1361-6463/ae6b9b','10.1063/5.0205196','10.1002/app.55612',
 '10.1063/5.0211580','10.1016/j.apsusc.2020.147091','10.1177/0021998320942575',
 '10.1002/adfm.201900412','10.1016/j.compositesb.2020.107855','10.1177/09540083211046456',
 '10.1177/09673911221110143','10.1016/j.cej.2018.04.196','10.1002/pc.28316',
 '10.1063/1.5121349','10.1080/15440478.2021.1966568','10.1002/smll.75841','10.1002/pc.70149',
]
log = json.load(open(LOGP, encoding='utf-8')) if os.path.exists(LOGP) else {}
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'}

def get(url, timeout=30, binary=False, retries=1):
    last=None
    for _ in range(retries+1):
        try:
            req=urllib.request.Request(url, headers=UA)
            d=urllib.request.urlopen(req,timeout=timeout,context=ctx).read()
            return d if binary else d.decode('utf-8','replace')
        except Exception as e:
            last=f'{type(e).__name__}: {str(e)[:100]}'
            time.sleep(1.0)
    raise RuntimeError(last)

def slug(d): return d.replace('/','_')

for doi in TARGETS:
    if doi in log and str(log[doi].get('outcome','')).startswith(('saved','pdf')):
        continue
    r = {'candidates': []}
    # OpenAlex
    try:
        j = json.loads(get(f'https://api.openalex.org/works/https://doi.org/{doi}'))
        for loc in (j.get('locations') or []):
            p = loc.get('pdf_url') or ''
            if p:
                r['candidates'].append(('openalex:' + (loc.get('source') or {}).get('display_name','?'), p))
        oa = j.get('open_access') or {}
        r['is_oa'] = oa.get('is_oa'); r['oa_status'] = oa.get('oa_status')
    except Exception as e:
        r['openalex'] = f'err {type(e).__name__}'
    # Semantic Scholar
    try:
        j = json.loads(get(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,title'))
        p = (j.get('openAccessPdf') or {}).get('url') or ''
        if p:
            r['candidates'].append(('s2', p))
    except Exception as e:
        r['s2'] = f'err {type(e).__name__}'
    # Unpaywall (valid-looking email)
    try:
        j = json.loads(get(f'https://api.unpaywall.org/v2/{doi}?email=sct.research.reader@gmail.com'))
        loc = j.get('best_oa_location') or {}
        p = loc.get('url_for_pdf') or loc.get('url') or ''
        if p:
            r['candidates'].append(('unpaywall', p))
    except Exception as e:
        r['unpaywall'] = f'err {type(e).__name__}'
    # try candidates
    seen = set()
    for route, url in r['candidates']:
        if url in seen: continue
        seen.add(url)
        if 'sci-hub' in url.lower(): continue
        try:
            data = get(url, timeout=45, binary=True, retries=0)
            if data[:4] == b'%PDF':
                path = os.path.join(PDFS, slug(doi) + '.pdf')
                open(path, 'wb').write(data)
                r['outcome'] = f'pdf:{route}'; r['pdf_url'] = url
                break
            else:
                txt = data.decode('utf-8','replace')
                if len(txt) > 20000 and re.search(r'\d\s*W\s*[·⋅/ ]?\s*m', txt, re.I):
                    open(os.path.join(BASE,'fulltext',slug(doi)+'.txt'),'w',encoding='utf-8').write(
                        f'SOURCE doi={doi} FETCH={route} {url}\n' + txt)
                    r['outcome'] = f'saved:html:{route}'; break
        except Exception as e:
            r.setdefault('dl_fail', []).append(f'{route}: {type(e).__name__}')
    r.setdefault('outcome', 'failed:no-oa-or-dl')
    log[doi] = r
    json.dump(log, open(LOGP,'w',encoding='utf-8'), indent=1)
    print(doi, r['outcome'], 'cands=', len(r['candidates']), r.get('is_oa'), r.get('oa_status'))

print('\nDONE. saved:', [d for d,v in log.items() if str(v.get('outcome','')).startswith(('saved','pdf'))])
