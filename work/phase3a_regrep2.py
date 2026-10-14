# Phase 3A part 2: raw context dump for conductivity mentions
import re, os

FT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fulltext')

def dump(fname, pat, width=260, maxhits=40):
    path = os.path.join(FT, fname)
    text = open(path, encoding='utf-8', errors='replace').read()
    print(f'\n=== {fname}: /{pat}/ ===')
    n = 0
    for m in re.finditer(pat, text, re.IGNORECASE):
        s = m.start()
        ctx = text[max(0, s-40):s+width].replace('\n', ' | ')
        print(f'  ...{ctx}...')
        n += 1
        if n >= maxhits:
            print('  (truncated)')
            break
    print(f'  [{n} shown]')

# how is k written at all in these files?
for f in ['10.3390_nano9101396.txt', '10.1039_c8ra10645b.txt', '10.3390_polym10030277.txt']:
    dump(f, r'conductivit\w*\s*(?:coefficient|of|increas)', width=200, maxhits=15)

# search for any W followed within 15 chars by m and K in any form
for f in ['10.3390_nano9101396.txt', '10.1039_c8ra10645b.txt', '10.3390_polym10030277.txt',
          '10.3390_polym11071156.txt', '10.3390_molecules21050670.txt']:
    path = os.path.join(FT, f)
    text = open(path, encoding='utf-8', errors='replace').read()
    print(f'\n=== {f}: loose W..m..K scan ===')
    n = 0
    for m in re.finditer(r'W[\s\u00a0]{0,3}[/(]?[\s\u00a0]{0,2}m.{0,4}K', text):
        s = max(0, m.start()-60)
        ctx = text[s:m.end()+40].replace('\n', ' | ')
        print(f'  {m.group(0)!r} -> ...{ctx}...')
        n += 1
        if n >= 30:
            print('  (truncated)')
            break
    if n == 0:
        print('  NONE')

# ajps: is 0.23092 experimental or simulated?
dump('10.31248_ajps2025.124.txt', r'0\.23092|simulat|finite element|ANSYS|predicted|model(?:ed|ling)? (?:thermal|result)|measured', width=240, maxhits=25)
