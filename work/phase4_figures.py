"""Phase 4 Mission B: download figure images for figure-only papers via EPMC."""
import json, os, re, time, urllib.parse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, 'figures')
os.makedirs(FIG, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) thermal-curation-research/1.0'}

PAPERS = {
    '10.3390/polym11071156': 'PMC6680888',
    '10.3390/molecules21050670': 'PMC6273151',
}

def fetch(url, timeout=45, tries=2):
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

log = {}
for doi, pmcid in PAPERS.items():
    entry = {'pmcid': pmcid}
    # get figure list from fullTextXML
    ok, r = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML')
    if not ok:
        entry['xml'] = f'fail:{r}'
        log[doi] = entry
        continue
    xml = r.text
    # find <fig ...><label>Figure N</label> ... <graphic xlink:href="...">
    figs = re.findall(r'<fig\b[^>]*id="([^"]+)"[^>]*>(.*?)</fig>', xml, flags=re.S)
    flist = []
    for fid, body in figs:
        lab = re.search(r'<label>(.*?)</label>', body)
        href = re.search(r'xlink:href="([^"]+)"', body)
        cap = re.search(r'<caption>(.*?)</caption>', body, flags=re.S)
        cap_txt = re.sub(r'<[^>]+>', ' ', cap.group(1)) if cap else ''
        cap_txt = re.sub(r'\s+', ' ', cap_txt).strip()[:180]
        flist.append({
            'id': fid,
            'label': lab.group(1) if lab else '',
            'href': href.group(1) if href else '',
            'caption': cap_txt,
        })
    entry['figs'] = flist
    # download figures via EPMC static image endpoint
    saved = []
    for f in flist:
        href = f['href']
        if not href:
            continue
        # EPMC article images: https://europepmc.org/articles/PMCxxx/bin/<href>
        for base in (
            f'https://europepmc.org/articles/{pmcid}/bin/{href}',
            f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/bin/{href}',
        ):
            ok2, r2 = fetch(base, timeout=60)
            if ok2 and len(r2.content) > 3000:
                safe = href.replace('/', '_')
                path = os.path.join(FIG, f'{pmcid}_{safe}')
                with open(path, 'wb') as fh:
                    fh.write(r2.content)
                saved.append({'file': os.path.basename(path), 'label': f['label'], 'bytes': len(r2.content), 'caption': f['caption']})
                break
        else:
            saved.append({'file': None, 'label': f['label'], 'href': href, 'error': 'download_fail'})
    entry['saved'] = saved
    log[doi] = entry
    json.dump(log, open(os.path.join(BASE, 'phase4_figures_log.json'), 'w', encoding='utf-8'), indent=2)
    print(f'[{doi}] figs={len(flist)} saved={sum(1 for s in saved if s.get("file"))}')
    for s in saved:
        print('  ', s.get('label'), s.get('file'), s.get('bytes', s.get('error', '')), '|', s.get('caption', '')[:80])
print('done')
