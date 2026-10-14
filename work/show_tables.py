import re, sys

targets = [
    '10.3390_polym10030340', '10.3390_polym12020426', '10.3390_polym13060955',
    '10.3390_nano8040242', '10.1038_srep04779', '10.3390_polym10121412',
    '10.3390_polym13244417', '10.3390_nano11020373',
]
if len(sys.argv) > 1:
    targets = sys.argv[1:]

for t in targets:
    txt = open(rf'work\fulltext\{t}.txt', encoding='utf-8', errors='replace').read()
    print('#' * 110)
    print('#', t)
    seen = set()
    for m in re.finditer(r'\[TABLE.*?\[/TABLE\]', txt, flags=re.S):
        b = m.group(0)
        key = b[:120]
        if key in seen:
            continue
        seen.add(key)
        print(b[:3500])
        print('---')
