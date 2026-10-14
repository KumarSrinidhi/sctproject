"""Phase 2 inspect #2: drop-row confidences, label-row details, phase1 row findings."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

inp = json.load(open('work/audit_phase2_inputs.json', encoding='utf-8'))
rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
by_id = {r['row_id']: r for r in rows}
p1 = json.load(open('work/audit_phase1_rows.json', encoding='utf-8'))
# normalize p1 structure
if isinstance(p1, dict):
    print('p1 keys:', list(p1.keys())[:10])
    rows1 = p1.get('rows') or p1.get('row_results') or p1
else:
    rows1 = p1
if isinstance(rows1, dict):
    # maybe row_id -> record
    get1 = lambda rid: rows1.get(rid)
else:
    rows1 = {r.get('row_id'): r for r in rows1}
    get1 = lambda rid: rows1.get(rid)

drops = (inp['drop_intra_recommended'] + inp['drop_cross_recommended']
         + inp['drop_out_of_scope_recommended'])
print('-- drop rows: confidence + k --')
for d in drops:
    r = by_id[d]
    print(f"{d}: conf={r['confidence']} k={r['k_composite_W_mK']} doi={r['doi']}")

print('\n-- label target rows (full) --')
for suf in ['036','147','180','095','152','153','188','151']:
    for k, r in by_id.items():
        if k.endswith('-'+suf):
            print(f"{k}: filler_material={r['filler_material']!r}")
            print(f"    original={r['filler_material_original']!r}")
            print(f"    matrix={r['matrix_polymer']!r} notes={r['notes'][:160]!r}")

print('\n-- existing rows containing hybrid in filler_material --')
for r in rows:
    if 'hybrid' in r['filler_material'].lower():
        print(f"  {r['row_id']}: {r['filler_material']!r}")

print('\n-- filler_material=none rows --')
for r in rows:
    if r['filler_material'] in ('none', 'neat'):
        print(f"  {r['row_id']}: {r['filler_material']!r} orig={r['filler_material_original']!r}")

print('\n-- phase1 findings for label rows --')
for suf in ['036','147','180','095','151','152','153','188','159']:
    rec = None
    if isinstance(rows1, dict) and not any(isinstance(v, dict) and 'status' in v for v in list(rows1.values())[:1]):
        pass
    for k, v in (rows1.items() if isinstance(rows1, dict) else []):
        if k.endswith('-'+suf):
            rec = (k, v)
    if rec:
        print(f'{rec[0]}: {json.dumps(rec[1], ensure_ascii=False)[:400]}')
    else:
        print(f'suffix {suf}: NOT FOUND in phase1 rows')
