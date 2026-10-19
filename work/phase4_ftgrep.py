import json, re, sys

def load(p):
    t = open(p, encoding='utf-8').read()
    try:
        s = json.loads(t)
        if isinstance(s, str):
            return s
    except Exception:
        pass
    return t

path = sys.argv[1]
t = load(path)
# save as txt alongside
if path.endswith('.json'):
    open(path[:-5] + '.txt', 'w', encoding='utf-8').write(t)
print('len', len(t))
pats = sys.argv[2].split(',') if len(sys.argv) > 2 else ['1.26']
for pat in pats:
    hits = [m.start() for m in re.finditer(re.escape(pat), t)]
    print(f'== {pat} ({len(hits)} hits)')
    for i in hits[:6]:
        print('   ', t[max(0, i-160):i+120].replace('\n', ' '))
