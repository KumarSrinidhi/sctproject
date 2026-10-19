import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
hits = json.load(open(os.path.join(BASE, 'phase3c_abstract_hits.json'), encoding='utf-8'))
EPX = ('epox', 'bisphenol', 'dgeba')
for e in hits:
    if not e.get('k_hits'):
        continue
    t = ((e.get('title') or '') + ' ' + e.get('abstract', '')).lower()
    if not any(k in t for k in EPX):
        print('SKIP (not epoxy):', e['doi'], (e.get('title') or '')[:70])
        continue
    print('=' * 110)
    print(e['doi'], '|', (e.get('title') or '')[:110])
    print('ABSTRACT:', (e.get('abstract') or '')[:1300])
    print('--- k contexts:')
    for h in e['k_hits'][:6]:
        print('  >>', h[:230])
