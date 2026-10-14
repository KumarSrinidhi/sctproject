"""Phase 2 pre-flight:
1. Snapshot SHA-256 of protected source docs (fulltext/, extract_*.py, io_append.py, build_deliverables.py).
2. Dry-run regeneration of the 4 derived CSVs from current JSONL; byte-compare vs on-disk.
   Proves the Phase 2 regeneration pipeline is byte-faithful before any edit is applied.
Exit 0 = all good.
"""
import json, csv, hashlib, sys, tempfile, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path('work')
OUT = Path('.')
ok = True

# ---- 1. source-doc hashes ----
h = {}
for p in sorted((BASE / 'fulltext').glob('*')):
    h[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted(BASE.glob('extract_*.py')):
    h[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['io_append.py', 'build_deliverables.py']:
    p = BASE / name
    h[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
json.dump(h, open(BASE / 'phase2_source_hashes_before.json', 'w'), indent=1)
print(f'source docs hashed: {len(h)} (fulltext + extract_*.py + io_append.py + build_deliverables.py)')

# ---- 2. dry-run regen byte-compare ----
COLS = ['row_id', 'doi', 'source_url', 'paper_title', 'year', 'matrix_polymer', 'curing_agent',
        'filler_material', 'filler_material_original', 'filler_shape', 'filler_aspect_ratio',
        'filler_mean_size_um', 'size_distribution', 'filler_loading_vol_pct', 'filler_loading_wt_pct',
        'filler_loading_original_value', 'filler_loading_original_unit', 'functionalization',
        'filler_alignment', 'processing_method', 'k_matrix_W_mK', 'k_composite_W_mK', 'k_direction',
        'measurement_method', 'measurement_temperature_C', 'k_original_value', 'k_original_unit',
        'value_source', 'source_location', 'confidence', 'notes']

rows = [json.loads(l) for l in open(BASE / 'rows_raw.jsonl', encoding='utf-8')]
log = [json.loads(l) for l in open(BASE / 'extraction_log.jsonl', encoding='utf-8')]

tmp = Path(tempfile.mkdtemp())

# dataset
with open(tmp / 'thermal_conductivity_dataset.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
    for r in rows: w.writerow(r)

# inventory (same logic as build_deliverables)
papers = {}
for r in rows:
    d = r['doi']
    if d not in papers:
        papers[d] = {'doi': d, 'paper_title': r['paper_title'], 'year': r['year'],
                     'source_url': r['source_url'], 'rows_extracted': 0,
                     'filler_materials': set(), 'matrix_polymers': set(), 'k_min': 999, 'k_max': 0}
    p = papers[d]; p['rows_extracted'] += 1
    p['filler_materials'].add(r['filler_material']); p['matrix_polymers'].add(r['matrix_polymer'])
    k = float(r['k_composite_W_mK']); p['k_min'] = min(p['k_min'], k); p['k_max'] = max(p['k_max'], k)
inv_cols = ['doi','paper_title','year','source_url','rows_extracted','filler_materials','matrix_polymers','k_min_W_mK','k_max_W_mK']
with open(tmp / 'paper_inventory.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=inv_cols); w.writeheader()
    for d in sorted(papers, key=lambda x: papers[x]['doi']):
        p = papers[d]
        w.writerow({'doi': p['doi'], 'paper_title': p['paper_title'], 'year': p['year'],
                    'source_url': p['source_url'], 'rows_extracted': p['rows_extracted'],
                    'filler_materials': '; '.join(sorted(p['filler_materials'])),
                    'matrix_polymers': '; '.join(sorted(p['matrix_polymers'])),
                    'k_min_W_mK': p['k_min'], 'k_max_W_mK': p['k_max']})

# extraction log
log_cols = ['candidate_id','doi','paper_title','date_processed','access_result','files_inspected',
            'tables_inspected','figures_inspected','candidate_measurements','rows_appended',
            'unit_conversions','duplicate_checks','qc_findings','rows_rejected_at_append']
with open(tmp / 'extraction_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=log_cols, extrasaction='ignore'); w.writeheader()
    for e in log:
        row = {c: e.get(c, '') for c in log_cols}
        rej = e.get('rows_rejected_at_append', [])
        if rej:
            row['rows_rejected_at_append'] = '; '.join(f'{rid}:{reason}' for rid, reason in rej)
        w.writerow(row)

# uncertain
with open(tmp / 'uncertain_measurements.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
    for r in rows:
        if r['confidence'] != 'High':
            w.writerow(r)

for name in ['thermal_conductivity_dataset.csv', 'paper_inventory.csv',
             'extraction_log.csv', 'uncertain_measurements.csv']:
    a = (tmp / name).read_bytes()
    b = (OUT / name).read_bytes()
    same = a == b
    ok &= same
    print(f'dry-run byte-compare {name}: {"IDENTICAL" if same else "MISMATCH"} ({len(a)} vs {len(b)} bytes)')

print('PRE-FLIGHT', 'OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
