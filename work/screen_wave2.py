import json, os, re, sys

WORK = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(WORK, 'fulltext')
targets = json.load(open(os.path.join(WORK, 'wave2_fetch.json'), encoding='utf-8'))
targets = [t['doi'] for t in targets if t['status'] in ('ok', 'have')]

# k value sentence extraction
pat = re.compile(r'[^.\n]{0,160}?(?:thermal conductivity|TC|k(?:_\w+)?)[^.\n]{0,60}?'
                 r'(?:reached|achieved|obtained|was|were|of|up to|as (?:high|low) as|increased to|to)\s*'
                 r'=?\s*([0-9]\.?[0-9]*)\s*(?:±\s*[0-9.]+\s*)?W\s*(?:·|/|m?\s*)\s*m?[\s·]*[Kk](?:\s*[·\-]\s*1?\s*[Kk])?'
                 r'[^.\n]{0,120}', re.I)
simple = re.compile(r'([0-9]+\.?[0-9]*)\s*(?:±\s*[0-9.]+\s*)?W\s*(?:·|/)?\s*m(?:\s*[·\-]|\s*)K(?:\s*[·\-]|\s*)1', re.I)
# k value sentence extraction — handle W/mK, W m−1 K−1, W·m−1·K−1, W/(m·K)
unit = r'(?:W\s*/\s*\(?m[\s·\-–]*K\)?|W\s*m\s*[−\-–−]\s*1\s*[·\-–]?\s*K\s*[·\-–]?\s*1|W\s*[·\-]\s*m\s*[−\-–]\s*1\s*[·\-]\s*K\s*[·\-]\s*1|W/mK|W/m\.K|W/(m\*K))'
simple2 = re.compile(r'([0-9]+\.?[0-9]*)\s*(?:±\s*[0-9.]+\s*)?' + unit, re.I)

report = []
for doi in targets:
    fn = doi.replace('/', '_') + '.txt'
    p = os.path.join(FULL, fn)
    if not os.path.exists(p):
        continue
    txt = open(p, encoding='utf-8', errors='replace').read()
    lines = txt.split('\n')
    # in-scope heuristics
    is_epoxy = bool(re.search(r'epoxy', txt[:8000], re.I))
    fillers = set()
    for f in ['boron nitride', 'h-BN', 'BN ', 'BNNS', 'AlN', 'aluminum nitride', 'Al2O3', 'alumina']:
        if re.search(re.escape(f), txt[:12000], re.I):
            fillers.add(f)
    hits = []
    for m in simple2.finditer(txt):
        a = max(0, m.start() - 200)
        ctx = txt[a:m.end() + 150].replace('\n', ' ')
        hits.append(ctx)
    # dedupe by value
    vals = {}
    for m in simple2.finditer(txt):
        v = float(m.group(1))
        a = max(0, m.start() - 220)
        ctx = re.sub(r'\s+', ' ', txt[a:m.end() + 130])
        vals.setdefault(v, ctx)
    report.append(dict(doi=doi, epoxy=is_epoxy, fillers=sorted(fillers), n_k=len(vals),
                       vals=dict(list(vals.items())[:14])))

report.sort(key=lambda r: -r['n_k'])
for r in report:
    print(f"{r['n_k']:3d} epoxy={int(r['epoxy'])} {r['doi']:42s} F={','.join(r['fillers'])[:50]}")
json.dump(report, open(os.path.join(WORK, 'wave2_screen.json'), 'w', encoding='utf-8'), indent=1)
print('saved wave2_screen.json')
