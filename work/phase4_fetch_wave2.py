"""Phase 4 Wave 2: OA-PDF hunting via Semantic Scholar + OpenAIRE for the 24 abstract-only DOIs.
Sci-Hub deliberately NOT used (project policy). Per-request errors: retry once, continue.
"""
import json, os, re, time, urllib.parse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
PDF = os.path.join(BASE, 'phase4_pdfs')
os.makedirs(FT, exist_ok=True)
os.makedirs(PDF, exist_ok=True)
LOG = os.path.join(BASE, 'phase4_fetch_log.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) thermal-curation-research/1.0'}

TARGET_DOIS = list(json.load(open(os.path.join(BASE, 'phase4_fetch_log.json'), encoding='utf-8')).keys())

def slug(doi):
    return doi.replace('/', '_')

def fetch(url, timeout=45, tries=2, stream=False):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            if r.status_code == 200:
                return True, r
            last = f'HTTP {r.status_code}'
            if 400 <= r.status_code < 500:
                return False, last
        except requests.exceptions.RequestException as e:
            last = f'{type(e).__name__}: {str(e)[:100]}'
        time.sleep(2 * (i + 1))
    return False, last

def pdf_to_text(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    return '\n'.join(p.get_text() for p in doc)

def try_download_pdf(doi, pdf_url, tag):
    ok, r = fetch(pdf_url, timeout=60)
    if not ok:
        return f'{tag}_dl_fail:{r}', None
    content = r.content
    if content[:4] != b'%PDF':
        return f'{tag}_not_pdf:{content[:10]!r}', None
    p = os.path.join(PDF, f'{slug(doi)}_{tag}.pdf')
    with open(p, 'wb') as f:
        f.write(content)
    try:
        text = pdf_to_text(p)
    except Exception as e:
        return f'{tag}_extract_fail:{e}', None
    if len(text) < 2000:
        return f'{tag}_too_short:{len(text)}', None
    tp = os.path.join(FT, f'{slug(doi)}_{tag}.txt')
    with open(tp, 'w', encoding='utf-8') as f:
        f.write(f'SOURCE: {tag} ({pdf_url})\nDOI: {doi}\n\n{text}\n')
    return f'{tag}_ok', {'url': pdf_url, 'chars': len(text), 'file': os.path.basename(tp)}

def s2_route(doi):
    url = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields=openAccessPdf,title,externalIds'
    ok, r = fetch(url)
    if not ok:
        return f's2_fail:{r}', None
    try:
        data = r.json()
    except Exception as e:
        return f's2_parse_fail:{e}', None
    oa = (data.get('openAccessPdf') or {}).get('url')
    if not oa:
        return 's2_no_oa', None
    return try_download_pdf(doi, oa, 's2oa')

def openaire_route(doi):
    url = f'https://api.openaire.eu/search/publications?doi={urllib.parse.quote(doi)}&format=json'
    ok, r = fetch(url)
    if not ok:
        return f'openaire_fail:{r}', None
    try:
        data = r.json()
    except Exception as e:
        return f'openaire_parse_fail:{e}', None
    # walk results for webresource urls ending in .pdf
    urls = []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('url', 'webresource_url') and isinstance(v, str):
                    urls.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    try:
        walk(data)
    except Exception:
        pass
    pdfs = [u for u in urls if '.pdf' in u.lower()]
    if not pdfs:
        return f'openaire_no_pdf(urls={len(urls)})', None
    for u in pdfs[:3]:
        st, detail = try_download_pdf(doi, u, 'openaire')
        if st.endswith('_ok'):
            return st, detail
    return f'openaire_all_failed:first={pdfs[0][:80]}', None

def main():
    log = json.load(open(LOG, encoding='utf-8'))
    for doi in TARGET_DOIS:
        entry = log[doi]
        if entry.get('status', '').endswith('_ok'):
            print(f'[skip-exists] {doi}')
            continue
        st, detail = s2_route(doi)
        entry['s2oa'] = {'status': st, 'detail': detail}
        if st.endswith('_ok'):
            entry['status'] = st
            log[doi] = entry
            json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
            print(f'[OK-s2] {doi} {detail}')
            continue
        st2, detail2 = openaire_route(doi)
        entry['openaire'] = {'status': st2, 'detail': detail2}
        if st2.endswith('_ok'):
            entry['status'] = st2
        else:
            entry['status'] = f"failed2(s2={st}; openaire={st2})"
        log[doi] = entry
        json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
        print(f'[done] {doi} -> {entry["status"]}')
    okc = sum(1 for e in log.values() if e.get('status','').endswith('_ok'))
    print(f'\nOK total: {okc}/{len(log)}')

if __name__ == '__main__':
    main()
