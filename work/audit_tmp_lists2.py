import csv, re

inv = list(csv.DictReader(open('paper_inventory.csv', encoding='utf-8-sig')))
log = list(csv.DictReader(open('extraction_log.csv', encoding='utf-8-sig')))
for d in ['10.1038/s41598-018-19945-3', '10.3390/polym17111507', '10.1039/c8ra10211b']:
    i = [x for x in inv if x['doi'] == d]
    l = [x for x in log if x['doi'] == d]
    print(d)
    print('  inv:', (i[0].get('paper_title') or i[0].get('title', ''))[:90] if i else 'ABSENT')
    print('  log:', (l[0].get('paper_title') or l[0].get('title', ''))[:90] if l else 'ABSENT')
print()

rows = list(csv.DictReader(open('thermal_conductivity_dataset.csv', encoding='utf-8-sig')))
s = open('thermal_conductivity_dataset.csv', encoding='utf-8-sig').read()
print('chemrxiv mention in dataset:', 'chemrxiv' in s.lower())
inv_s = open('paper_inventory.csv', encoding='utf-8-sig').read()
print('chemrxiv in inventory:', 'chemrxiv' in inv_s.lower())
for m in set(re.findall(r'10\.26434[^\s,"]*', inv_s)):
    print(' inv doi:', m)
log_s = open('extraction_log.csv', encoding='utf-8-sig').read()
for m in set(re.findall(r'10\.26434[^\s,"]*', log_s)):
    print(' log doi:', m)

for r in rows:
    if 'acs' in r['doi'] or '10.26434' in r['doi']:
        print(' row doi:', r['doi'], r['row_id'], '| notes:', r['notes'][:160])
