import json, os, re, time, ssl, urllib.request, urllib.parse, warnings

warnings.filterwarnings('ignore')
BASE = r'work'
FT = os.path.join(BASE, 'fulltext')
os.makedirs(FT, exist_ok=True)
LOGP = os.path.join(BASE, 'phase4_fetch2_log.json')

TARGETS = [
 '10.1039/d4dt00979g','10.1007/s10854-024-13657-3','10.1002/slct.202507155',
 '10.1016/j.compscitech.2020.108304','10.1016/j.compscitech.2020.108322','10.1002/pc.27985',
 '10.1016/j.jcomc.2020.100087','10.1002/pc.29136','10.1088/1361-6463/ae6b9b',
 '10.1063/5.0205196','10.1002/app.55612','10.1063/5.0211580','10.1016/j.apsusc.2020.147091',
 '10.1177/0021998320942575','10.1002/adfm.201900412','10.1016/j.compositesb.2020.107855',
 '10.1177/09540083211046456','10.1177/09673911221110143','10.1016/j.cej.2018.04.196',
 '10.1002/pc.28316','10.1063/1.5121349','10.1080/15440478.2021.1966568',
 '10.1002/smll.75841','10.1002/pc.70149',
]
# resume prior log if present
log = {}
if os.path.exists(LOGP):
    try:
        log = json.load(open(LOGP, encoding='utf-8'))
    except Exception:
        log = {}

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

def slug(doi): return doi.replace('/', '_')

def get(url, timeout=30, retries=1, headers=None, binary=False):
    last = None
    for attempt in range(retries + 1):
        for verify in (True, False):
            try:
                ctx = ssl.create_default_context()
                if not verify:
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers=headers or UA)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                    data = r.read()
                    return data if binary else data.decode('utf-8', 'replace')
            except Exception as e:
                last = f'{type(e).__name__}: {e}'
        time.sleep(1.5)
    raise RuntimeError(last or 'unknown')

def has_k_content(text):
    return bool(re.search(r'\d\s*\.?\d*\s*W\s*[·⋅/ ]?\s*m', text, re.I)) and len(text) > 15000

def save(doi, text, route):
    path = os.path.join(FT, slug(doi) + '.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'SOURCE doi={doi} FETCH={route}\n' + text)
    return path

results = {}
for doi in TARGETS:
    if doi in log and log[doi].get('outcome', '').startswith('saved'):
        results[doi] = log[doi]
        continue
    r = {}
    slugd = slug(doi)
    if os.path.exists(os.path.join(FT, slugd + '.txt')):
        r = {'outcome': 'saved:local_exists', 'route': 'local'}
        results[doi] = r; continue
    # 1. Europe PMC
    try:
        j = json.loads(get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{urllib.parse.quote(doi)}&format=json'))
        hit = (j.get('resultList', {}).get('result') or [{}])[0]
        pmcid = hit.get('pmcid')
        r['epmc_hits'] = j.get('hitCount', 0)
        if pmcid:
            xml = get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML')
            if has_k_content(xml):
                save(doi, xml, f'EPMC {pmcid} fullTextXML')
                r['outcome'] = 'saved:epmc'
                results[doi] = r; continue
            r['epmc'] = f'{pmcid} xml too small/no-k ({len(xml)})'
        else:
            r['epmc'] = 'no pmcid'
    except Exception as e:
        r['epmc'] = f'err {type(e).__name__}'
    # 2. Unpaywall
    try:
        j = json.loads(get(f'https://api.unpaywall.org/v2/{doi}?email=phase4@example.com'))
        loc = j.get('best_oa_location') or {}
        pdf = loc.get('url_for_pdf') or loc.get('url')
        r['unpaywall'] = bool(pdf)
        if pdf:
            try:
                data = get(pdf, binary=True, timeout=45)
                if data[:4] == b'%PDF':
                    with open(os.path.join(BASE, 'phase4_pdfs', slugd + '.pdf'), 'wb') as f:
                        f.write(data)
                    r['outcome'] = 'saved:pdf_' + pdf[:60]
                elif has_k_content(data.decode('utf-8', 'replace')):
                    save(doi, data.decode('utf-8', 'replace'), 'unpaywall-html ' + pdf[:60])
                    r['outcome'] = 'saved:unpaywall-html'
                else:
                    r['unpaywall_dl'] = f'garbage {data[:40]!r}'
            except Exception as e:
                r['unpaywall_dl'] = f'err {type(e).__name__}'
            if str(r.get('outcome','')).startswith('saved'):
                results[doi] = r; continue
    except Exception as e:
        r['unpaywall'] = f'err {type(e).__name__}'
    # 3. doi.org landing page
    try:
        html = get(f'https://doi.org/{doi}', timeout=35)
        if has_k_content(html):
            save(doi, html, 'doi.org landing')
            r['outcome'] = 'saved:landing'
            results[doi] = r; continue
        r['landing'] = f'len={len(html)} no-k'
    except Exception as e:
        r['landing'] = f'err {type(e).__name__}'
    r.setdefault('outcome', 'failed:all-python-routes')
    results[doi] = r
    json.dump(results, open(LOGP, 'w', encoding='utf-8'), indent=1)
    print(doi, r.get('outcome'), {k: v for k, v in r.items() if k != 'outcome'})

json.dump(results, open(LOGP, 'w', encoding='utf-8'), indent=1)
saved = [d for d, v in results.items() if str(v.get('outcome','')).startswith('saved')]
print('SAVED:', len(saved), saved)
print('FAILED:', len([d for d,v in results.items() if not str(v.get('outcome','')).startswith('saved')]))
