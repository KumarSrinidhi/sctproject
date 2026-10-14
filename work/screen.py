import os, re, json, glob

FT = r'work\fulltext'
files = sorted(glob.glob(os.path.join(FT, '*.txt')))
print('files:', len(files))
report = []
for fp in files:
    txt = open(fp, encoding='utf-8', errors='replace').read()
    title = re.search(r'TITLE: (.*)', txt)
    tables = re.findall(r'\[TABLE.*?\n(.*?)\[/TABLE\]', txt, flags=re.S)
    figs = len(re.findall(r'\[FIG\]', txt))
    rel_tables = 0
    for t in tables:
        tl = t.lower()
        if ('conductiv' in tl or 'w/m' in tl or 'w m' in tl or 'w·m' in tl) and \
           re.search(r'\d+\s*(wt\.?%|vol\.?%|phr)', tl):
            rel_tables += 1
    # quick scope check
    tl = txt.lower()
    scope = []
    if 'epoxy' in tl: scope.append('epoxy')
    if 'silicone' in tl: scope.append('silicone')
    if 'polyimide' in tl: scope.append('polyimide')
    if 'pdms' in tl or 'polydimethylsiloxane' in tl: scope.append('pdms')
    filler = []
    for k, lab in [('boron nitride', 'BN'), ('h-bn', 'BN'), ('bnns', 'BNNS'), ('aln', 'AlN'),
                   ('aluminum nitride', 'AlN'), ('alumina', 'Al2O3'), ('al2o3', 'Al2O3'),
                   ('silicon carbide', 'SiC'), ('sic', 'SiC'), ('silicon nitride', 'Si3N4')]:
        if k in tl:
            filler.append(lab)
    filler = sorted(set(filler))
    n_wc = len(re.findall(r'wt\.?\s?%', tl))
    n_vc = len(re.findall(r'vol\.?\s?%', tl))
    report.append({
        'file': os.path.basename(fp), 'chars': len(txt),
        'title': (title.group(1)[:80] if title else '?'),
        'tables': len(tables), 'rel_tables': rel_tables, 'figs': figs,
        'scope': scope, 'fillers': filler, 'wt_pct_mentions': n_wc, 'vol_pct_mentions': n_vc,
    })

report.sort(key=lambda r: (-r['rel_tables'], -r['tables']))
for r in report:
    print(f"{r['rel_tables']:2d}rt {r['tables']:2d}t {r['figs']:2d}f {r['chars']//1000:3d}k | {','.join(r['scope']) or '-':20s} | {','.join(r['fillers']) or '-':12s} | {r['file'][:46]}")
json.dump(report, open(r'work\screen_report.json', 'w', encoding='utf-8'), indent=1)
