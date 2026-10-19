import re
lines = open(r'work\extract_027.py', encoding='utf-8').read().splitlines()
for i, l in enumerate(lines, 1):
    if re.search(r"notes='[^']*',\s*$", l):
        print(i, l.rstrip()[-90:])
