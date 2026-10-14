import re, glob, os

files = sorted(glob.glob(r'work\fulltext\*.txt'))
for fp in files:
    txt = open(fp, encoding='utf-8', errors='replace').read()
    # table captions
    caps = re.findall(r'\[TABLE\] (Table[^|\n]*)', txt)
    # numeric k mentions in running text: value + W unit
    hits = []
    for m in re.finditer(r'[^.\n]{0,120}?(\d+\.?\d*)\s*(W\s*[·⋅]?\s*m\s*[−\-−\-1]{1,3}\s*[·⋅]?\s*K\s*[−\-−\-1]{0,3}|W\s*/\s*\(?m\s*[·⋅]?\s*K|W\s*m\s*−1\s*K\s*−1|W/(m·K)|W·m−1·K−1|W m−1 K−1)[^.\n]{0,80}', txt):
        s = m.group(0).strip().replace('\n', ' ')
        if re.search(r'wt\.?%|vol\.?%|phr|loading|filled|content', s, re.I):
            hits.append(s[:160])
    print('=' * 100)
    print(os.path.basename(fp))
    print(' TABLE CAPS:', ' || '.join(c.strip()[:70] for c in caps[:12]))
    print(' TEXT HITS:', len(hits))
    for h in hits[:14]:
        print('   *', h)
