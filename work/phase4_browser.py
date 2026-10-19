"""Phase 4 Missions A(route d)+C: browser rendering of blocked DOIs via Playwright connect_over_cdp.
Chrome must be running with --remote-debugging-port=9222.
Per-DOI: navigate doi.org -> wait -> innerText -> captcha check -> save full text or mark blocked.
Never abort the batch on one failure.
"""
import json, os, re, sys, time, traceback

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
LOG = os.path.join(BASE, 'phase4_browser_log.json')
os.makedirs(FT, exist_ok=True)

CAPTCHA_MARKERS = [
    'captcha', 'radware', 'are you a robot', 'are you human', 'verify you are',
    'access denied', 'just a moment', 'attention required', 'cloudflare',
    'incapsula', 'request unsuccessful', 'bot detection', 'automatic redirect',
    'pardon our interruption', 'checking your browser',
]

# Mission A: 24 abstract-only DOIs (upgrade priority), then Mission C: top blocked from unusable_sources
MISSION_A = [
    '10.1002/pc.29136', '10.1007/s10854-024-13657-3', '10.1088/1361-6463/ae6b9b',
    '10.1002/slct.202507155', '10.1063/5.0205196', '10.1002/app.55612',
    '10.1063/5.0211580', '10.1039/d4dt00979g', '10.1016/j.compscitech.2020.108304',
    '10.1016/j.apsusc.2020.147091', '10.1177/0021998320942575', '10.1002/adfm.201900412',
    '10.1016/j.compscitech.2020.108322', '10.1016/j.compositesb.2020.107855',
    '10.1177/09540083211046456', '10.1177/09673911221110143', '10.1016/j.cej.2018.04.196',
    '10.1002/pc.28316', '10.1002/pc.27985', '10.1016/j.jcomc.2020.100087',
    '10.1063/1.5121349', '10.1080/15440478.2021.1966568', '10.1002/smll.75841',
    '10.1002/pc.70149',
]
MISSION_C = [
    '10.1515/polyeng-2025-0193', '10.1002/pc.71726', '10.1002/pc.71558',
    '10.1002/app.56949', '10.1002/pat.70120', '10.1002/inf2.70139', '10.1002/pc.70279',
    '10.1016/j.compositesa.2026.110044', '10.1016/j.compositesb.2025.112764',
    '10.1016/j.cej.2026.180373', '10.1016/j.carbon.2026.121402',
    '10.1016/j.porgcoat.2025.109667', '10.1016/j.ceramint.2026.04.021',
    '10.1016/j.apsusc.2025.163268', '10.1016/j.eurpolymj.2024.113084',
    '10.1016/j.matlet.2025.139278', '10.1016/j.compstruct.2025.119723',
    '10.1007/s10853-026-12616-z', '10.1007/s10854-026-18087-x',
    '10.1021/acsapm.4c01099', '10.1177/09540083251319488',
    '10.1088/1361-6528/ac0470', '10.1088/1742-6596/1003/1/012082',
]

def slug(doi):
    return doi.replace('/', '_')

def looks_blocked(text):
    low = text[:8000].lower()
    hits = [m for m in CAPTCHA_MARKERS if m in low]
    return hits

def try_doi(ctx, doi, log):
    if doi in log and log[doi].get('status') == 'content_ok':
        print(f'[skip-exists] {doi}')
        return
    page = ctx.new_page()
    entry = {}
    try:
        page.goto(f'https://doi.org/{doi}', timeout=45000, wait_until='domcontentloaded')
        page.wait_for_timeout(2500)
        final_url = page.url
        title = page.title()
        text = page.evaluate('() => document.body ? document.body.innerText : ""')
        blocked = looks_blocked(text or '')
        entry['final_url'] = final_url
        entry['title'] = title[:120]
        entry['chars'] = len(text or '')
        if blocked:
            entry['status'] = 'blocked_captcha'
            entry['markers'] = blocked
        elif not text or len(text) < 500:
            entry['status'] = 'empty_page'
        else:
            # k-relevance screen: thermal conductivity mentions
            k_hits = len(re.findall(r'thermal conductivity|W\s*\(?\s*m', text, flags=re.I))
            entry['k_hits'] = k_hits
            entry['status'] = 'content_ok'
            path = os.path.join(FT, slug(doi) + '_browser.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f'SOURCE: browser-rendered DOI landing ({final_url})\nDOI: {doi}\nTITLE: {title}\n\n{text}\n')
            entry['file'] = os.path.basename(path)
    except Exception as e:
        entry['status'] = 'nav_error'
        entry['error'] = f'{type(e).__name__}: {str(e)[:200]}'
    finally:
        try:
            page.close()
        except Exception:
            pass
    log[doi] = entry
    json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
    print(f'[{entry["status"]}] {doi}  {entry.get("final_url", entry.get("error",""))[:90]}')

def main(batch):
    from playwright.sync_api import sync_playwright
    log = {}
    if os.path.exists(LOG):
        log = json.load(open(LOG, encoding='utf-8'))
    dois = MISSION_A if batch == 'A' else MISSION_C
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        for doi in dois:
            try:
                try_doi(ctx, doi, log)
            except Exception as e:
                print(f'[FATAL-skip] {doi}: {e}')
                log[doi] = {'status': 'fatal', 'error': traceback.format_exc()[-300:]}
                json.dump(log, open(LOG, 'w', encoding='utf-8'), indent=2)
    from collections import Counter
    c = Counter(e.get('status') for e in log.values())
    print('\nSUMMARY:', json.dumps(dict(c), indent=2))

if __name__ == '__main__':
    batch = sys.argv[1] if len(sys.argv) > 1 else 'A'
    main(batch)
