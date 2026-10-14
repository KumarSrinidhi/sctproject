from pathlib import Path
import csv
from collections import Counter

files = ['thermal_conductivity_dataset.csv','paper_inventory.csv','extraction_log.csv',
         'uncertain_measurements.csv','unusable_sources.csv','quality_control_report.md','README.md']
for f in files:
    p = Path(f)
    status = 'OK' if p.exists() else 'MISSING'
    size = p.stat().st_size if p.exists() else 0
    print(f'{status}: {f} ({size} bytes)')

print()
with open('thermal_conductivity_dataset.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
print('dataset rows:', len(rows))
print('first:', rows[0]['row_id'], rows[0]['doi'])
print('last:', rows[-1]['row_id'], rows[-1]['doi'])
ks = [float(r['k_composite_W_mK']) for r in rows]
print('k range:', min(ks), '-', max(ks))
print('confidence:', Counter(r['confidence'] for r in rows))
print('value_source:', Counter(r['value_source'] for r in rows))
