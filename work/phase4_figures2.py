"""Phase 4 Mission B wave2: figure images via PMC OA FTP service and mdpi-res.com."""
import json, os, re, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, 'figures')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) thermal-curation-research/1.0'}

def fetch(url, timeout=60, tries=2):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                return True, r
            last = f'HTTP {r.status_code}'
            if 400 <= r.status_code < 500:
                return False, last
        except requests.exceptions.RequestException as e:
            last = f'{type(e).__name__}: {str(e)[:100]}'
        time.sleep(2 * (i + 1))
    return False, last

def try_save(url, outpath, minbytes=5000):
    ok, r = fetch(url)
    if not ok:
        return f'fail:{r}'
    c = r.content
    if len(c) < minbytes:
        return f'too_small:{len(c)}'
    ct = r.headers.get('Content-Type', '')
    head = c[:20]
    is_img = head[:3] == b'\xff\xd8\xff' or head[:8] == b'\x89PNG\r\n\x1a\n' or head[:4] == b'GIF8' or b'image' in ct.encode()
    if not is_img:
        return f'not_image:ct={ct}:head={head[:12]!r}'
    with open(outpath, 'wb') as f:
        f.write(c)
    return f'ok:{len(c)}'

log = {}

# --- 1. PMC OA web service: get tar.gz link, we only need figure files ---
for doi, pmcid in [('10.3390/polym11071156', 'PMC6680888'), ('10.3390/molecules21050670', 'PMC6273151')]:
    entry = {}
    ok, r = fetch(f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}')
    entry['oa_fcgi'] = (r.text[:500] if ok else str(r))
    print(f'[{pmcid}] oa_fcgi:', 'ok' if ok else r)
    if ok:
        m = re.search(r'href="([^"]+\.tar\.gz)"', r.text)
        if m:
            entry['tarball'] = m.group(1)
            print('  tarball:', m.group(1))
    log[doi] = entry

json.dump(log, open(os.path.join(BASE, 'phase4_figures_log2.json'), 'w', encoding='utf-8'), indent=2)

# --- 2. mdpi-res.com direct figure URLs ---
# MDPI pattern: https://mdpi-res.com/d_attachment/<journal>/<journal-volume-issue>/article_deploy/<filename>-gNNN.png
MDPI_TARGETS = {
    '10.3390/polym11071156': {
        'dir': 'polymers',
        'stem': 'polymers-11-01156',
        'figs': ['g011', 'g001'],  # Figure 11 = k plot (main target); Fig1 for sanity
    },
    '10.3390/molecules21050670': {
        'dir': 'molecules',
        'stem': 'molecules-21-00670',
        'figs': ['g003', 'g002', 'g006'],  # Fig 3 = k vs content; Fig2 GPTMS; Fig6 fit
    },
}
for doi, spec in MDPI_TARGETS.items():
    entry = log.get(doi, {})
    saved = []
    for fig in spec['figs']:
        got = None
        for ext in ('png', 'jpg'):
            url = f"https://mdpi-res.com/d_attachment/{spec['dir']}/{spec['stem']}/article_deploy/{spec['stem']}-{fig}.{ext}"
            out = os.path.join(FIG, f"{spec['stem']}-{fig}.{ext}")
            res = try_save(url, out)
            print(f'  {fig}.{ext}: {res}')
            if res.startswith('ok'):
                got = {'file': os.path.basename(out), 'result': res, 'url': url}
                break
        if not got:
            got = {'file': None, 'fig': fig, 'result': 'all_fail'}
        saved.append(got)
    entry['mdpi'] = saved
    log[doi] = entry
    json.dump(log, open(os.path.join(BASE, 'phase4_figures_log2.json'), 'w', encoding='utf-8'), indent=2)

print('\nSaved images:')
for f in os.listdir(FIG):
    p = os.path.join(FIG, f)
    with open(p, 'rb') as fh:
        head = fh.read(4)
    print(' ', f, os.path.getsize(p), 'JPEG' if head[:3]==b'\xff\xd8\xff' else 'PNG' if head[:4]==b'\x89PNG' else head)
