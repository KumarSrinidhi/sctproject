"""Phase 4 Mission A/C browser fetch driver using chrome-devtools via subprocess-free
direct calls is done manually by agent; this script only handles the text extraction
from pages after navigation. Agent navigates page, then calls this to save innerText.

Actually: simpler to just do navigate+evaluate_script via chrome-devtools MCP, then
agent writes the returned text to file. This script just normalizes/saves a list of
{doi, text} records already captured, into phase4_browser/<slug>.txt and updates
phase4_browser_log.json.
"""
import json, os, sys, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phase4_browser')
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phase4_browser_log.json')
os.makedirs(OUT, exist_ok=True)

CAPTCHA_MARKERS = ['captcha', 'radware', 'access denied', 'robot check', 'verify you are human',
                   'unusual traffic', 'are you a robot', 'enable javascript and cookies']

def looks_blocked(text):
    low = text[:8000].lower()
    return any(m in low for m in CAPTCHA_MARKERS)

def save(doi, text):
    slug = doi.replace('/', '_')
    path = os.path.join(OUT, slug + '.txt')
    blocked = looks_blocked(text)
    status = 'blocked' if blocked else ('success' if len(text) > 500 else 'too_short')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    # update log
    log = {}
    if os.path.exists(LOG):
        with open(LOG, encoding='utf-8') as f:
            log = json.load(f)
    log[doi] = {'status': status, 'chars': len(text), 'path': path}
    with open(LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)
    print(f"{doi}: {status} ({len(text)} chars)")
    return status

if __name__ == '__main__':
    # test from stdin JSON list of {doi, text}
    records = json.load(sys.stdin)
    for r in records:
        save(r['doi'], r['text'])
