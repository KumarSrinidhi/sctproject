"""Phase 4 Mission A: fetch full texts for abstract-only Medium rows (24 DOIs).
Routes per DOI (in order): EPMC fullTextXML -> Unpaywall OA PDF -> (webfetch/browser handled later).
Per-request TLS/network errors: retry once, then mark failed and CONTINUE. Never abort the batch.
"""
import json, os, re, time, ssl, traceback
import urllib.request, urllib.parse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
PDF = os.path.join(BASE, 'phase4_pdfs')
os.makedirs(FT, exist_ok=True)
os.makedirs(PDF, exist_ok=True)
LOG = os.path.join(BASE, 'phase4_fetch_log.json')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) thermal-curation-research/1.0'}

# The 24 Phase-3C abstract-only DOIs
TARGET_DOIS = [
    '10.1002/pc.29136',
    '10.1007/s10854-024-13657-3',
    '10.1088/1361-6463/ae6b9b',
    '10.1002/slct.202507155',
    '10.1063/5.0205196',
    '10.1002/app.55612',
    '10.1063/5.0211580',
    '10.1039/d4dt00979g',
    '10.1016/j.compscitech.2020.108304',
    '10.1016/j.apsusc.2020.147091',
    '10.1177/0021998320942575',
    '10.1002/adfm.201900412',
    '10.1016/j.compscitech.2020.108322',
    '10.1016/j.compositesb.2020.107855',
    '10.1177/09540083211046456',
    '10.1177/09673911221110143',
    '10.1016/j.cej.2018.04.196',
    '10.1002/pc.28316',
    '10.1002/pc.27985',
    '10.1016/j.jcomc.2020.100087',
    '10.1063/1.5121349',
    '10.1080/15440478.2021.1966568',
    '10.1002/smll.75841',
    '10.1002/pc.70149',
]

def slug(doi):
    return doi.replace('/', '_').replace(' ', '_')

def fetch(url, timeout=40, tries=2):
    """requests get with one retry on TLS/network errors. Returns (ok, bytes_or_err)."""
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            if r.status_code == 200:
                return True, r.content
            last = f'HTTP {r.status_code}'
            # 4xx: no point retrying
            if 400 <= r.status_code < 500:
                return False, last
        except requests.exceptions.RequestException as e:
            last = f'{type(e).__name__}: {e}'
        time.sleep(2 * (i + 1))
    return False, last

def xml_to_text(xml_bytes):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml_bytes, 'lxml-xml')
    # remove refs/xrefs noise
    for tag in soup.find_all(['xref', 'graphic', 'inline-graphic']):
        tag.decompose()
    title = soup.find('article-title')
    head = title.get_text(' ', strip=True) if title else ''
    body = soup.find('body')
    text = body.get_text('\n', strip=True) if body else soup.get_text('\n', strip=True)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return head, text

def epmc_route(doi):
    """EPMC: DOI search -> PMCID -> fullTextXML. Returns (status, detail)."""
    q = urllib.parse.quote(f'DOI:"{doi}"')
    ok, body = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json')
    if not ok:
        return f'epmc_search_fail:{body}', None
    try:
        data = json.loads(body)
        results = data.get('resultList', {}).get('result', [])
    except Exception as e:
        return f'epmc_search_parse_fail:{e}', None
    pmcid = None
    for res in results:
        if res.get('pmcid'):
            pmcid = res['pmcid']
            break
    if not pmcid:
        return f'epmc_no_pmcid(hits={len(results)})', None
    ok, xb = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML')
    if not ok:
        return f'epmc_fulltext_fail:{xb}', None
    if b'<body' not in xb and b'<article' not in xb:
        return f'epmc_fulltext_not_xml({len(xb)}b)', None
    head, text = xml_to_text(xb)
    path = os.path.join(FT, slug(doi) + '_epmc.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'SOURCE: Europe PMC fullTextXML {pmcid} (DOI {doi})\nTITLE: {head}\n\n{text}\n')
    return 'epmc_fulltext_ok', {'pmcid': pmcid, 'chars': len(text), 'file': os.path.basename(path)}

def pdf_to_text(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text())
    return '\n'.join(parts)

def unpaywall_route(doi):
    ok, body = fetch(f'https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=research.curation@gmail.com')
    if not ok:
        return f'unpaywall_fail:{body}', None
    try:
        data = json.loads(body)
    except Exception as e:
        return f'unpaywall_parse_fail:{e}', None
    loc = data.get('best_oa_location') or {}
    pdf_url = loc.get('url_for_pdf')
    landing = loc.get('url')
    host = loc.get('host_type')
    if not pdf_url and not landing:
        return 'unpaywall_no_oa', None
    if pdf_url:
        ok, content = fetch(pdf_url, timeout=60)
        if ok and content[:4] == b'%PDF':
            p = os.path.join(PDF, slug(doi) + '.pdf')
            with open(p, 'wb') as f:
                f.write(content)
            try:
                text = pdf_to_text(p)
                tp = os.path.join(FT, slug(doi) + '_oa.txt')
                with open(tp, 'w', encoding='utf-8') as f:
                    f.write(f'SOURCE: Unpaywall OA PDF ({host}) {pdf_url}\nDOI: {doi}\n\n{text}\n')
                return 'unpaywall_pdf_ok', {'url': pdf_url, 'chars': len(text), 'file': os.path.basename(tp)}
            except Exception as e:
                return f'unpaywall_pdf_extract_fail:{type(e).__name__}:{e}', None
        return f'unpaywall_pdf_download_fail:{content if isinstance(content,str) else content[:4]}', None
    # landing page only: record for later webfetch/browser wave
    return 'unpaywall_landing_only', {'landing': landing, 'host': host}

def main():
    log = {}
    if os.path.exists(LOG):
        log = json.load(open(LOG, encoding='utf-8'))
    for doi in TARGET_DOIS:
        if doi in log and log[doi].get('status', '').endswith('_ok'):
            print(f'[skip-exists] {doi} -> {log[doi]["status"]}')
            continue
        entry = {}
        status, detail = epmc_route(doi)
        entry['epmc'] = {'status': status, 'detail': detail}
        if status == 'epmc_fulltext_ok':
            entry['status'] = 'epmc_fulltext_ok'
            log[doi] = entry
            json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
            print(f'[OK-epmc] {doi} {detail}')
            continue
        status2, detail2 = unpaywall_route(doi)
        entry['unpaywall'] = {'status': status2, 'detail': detail2}
        if status2 == 'unpaywall_pdf_ok':
            entry['status'] = 'unpaywall_pdf_ok'
        else:
            entry['status'] = f"failed(epmc={entry['epmc']['status']}; unpaywall={status2})"
        log[doi] = entry
        json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
        print(f'[done] {doi} -> {entry["status"]}')
    # summary
    from collections import Counter
    c = Counter(e.get('status') for e in log.values())
    print('\nSUMMARY:', json.dumps(dict(c), indent=2))

if __name__ == '__main__':
    main()
