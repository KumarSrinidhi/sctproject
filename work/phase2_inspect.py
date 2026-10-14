"""Phase 2 inspect: dump current state of every row touched by approved changes."""
import json, csv, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
inp = json.load(open('work/audit_phase2_inputs.json', encoding='utf-8'))
rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
by_id = {r['row_id']: r for r in rows}

print(f'rows_raw.jsonl: {len(rows)} rows, unique ids: {len(by_id)}')

# 1. drop lists
drops = (inp['drop_intra_recommended'] + inp['drop_cross_recommended']
         + inp['drop_out_of_scope_recommended'])
missing = [d for d in drops if d not in by_id]
print(f'drops: {len(drops)} listed, missing from rows_raw: {missing}')

# 2. title fixes: rows per DOI + current title match
print('\n-- title fix DOIs --')
for doi, tf in inp['title_fixes'].items():
    rws = [r for r in rows if r['doi'] == doi]
    cur = {r['paper_title'] for r in rws}
    ok = all(r['paper_title'] == tf['current'] for r in rws)
    print(f'{doi}: {len(rws)} rows, all_current={ok}, rows={[r["row_id"] for r in rws]}')
    if not ok:
        print(f'   MISMATCH cur={cur}')

# 3. loading fixes
print('\n-- loading fixes --')
for lf in inp['loading_fixes']:
    rid = lf['row_id']
    r = by_id.get(rid)
    if not r:
        print(f'{rid}: MISSING'); continue
    print(f"{rid}: wt={r['filler_loading_wt_pct']!r} vol={r['filler_loading_vol_pct']!r} "
          f"orig_val={r['filler_loading_original_value']!r} orig_unit={r['filler_loading_original_unit']!r} "
          f"| stored={lf['stored_wt_pct']} -> {lf['corrected_wt_pct']} (dropped={rid in drops})")

# 4. non-numeric cells
print('\n-- numeric col violations --')
for nv in inp['numeric_col_violations']:
    r = by_id.get(nv['row_id'])
    print(f"{nv['row_id']}: col={nv['column']} value={nv['value']!r} actual={r.get(nv['column'])!r} "
          f"dropped={nv['row_id'] in drops} notes={r['notes'][:80]!r}")

# 5. unparsable strings
print('\n-- unparsable original strings --')
for u in inp['unparsable_original_strings']:
    r = by_id.get(u['row_id'])
    print(f"{u['row_id']}: orig_val={r['filler_loading_original_value']!r} unit={r['filler_loading_original_unit']!r} "
          f"wt={r['filler_loading_wt_pct']!r} vol={r['filler_loading_vol_pct']!r} "
          f"| json wt={u['numeric_wt']!r} vol={u['numeric_vol']!r} dropped={u['row_id'] in drops}")

# 6. sample label rows
print('\n-- sample label / hybrid convention rows --')
for rid in ['24638d02-036', 'a6f3a67e-147', '5b3a6f86-180', '0e680d76-095',
            '4a11b03c-151', '4a11b03c-152', '4a11b03c-153', '95307a1b-188']:
    r = by_id.get(rid)
    if not r:
        # find by suffix
        cand = [k for k in by_id if k.endswith('-' + rid.split('-')[-1])]
        print(f'{rid}: NOT FOUND, suffix candidates: {cand}')
        continue
    print(f"{rid}: doi={r['doi']} filler_mat={r['filler_material']!r} "
          f"orig={r['filler_material_original']!r} dropped={rid in drops}")

# show all rows whose id suffix matches
print('\n-- rows by suffix (036/147/180/095/151/152/153/188) --')
for suf in ['036','147','180','095','151','152','153','188']:
    m = [k for k in by_id if k.endswith('-'+suf)]
    for k in m:
        r = by_id[k]
        print(f"{k}: doi={r['doi']} filler_mat={r['filler_material']!r} orig={r['filler_material_original']!r}")

# 7. confidence / k range baseline
confs = {}
for r in rows:
    confs[r['confidence']] = confs.get(r['confidence'], 0) + 1
ks = [float(r['k_composite_W_mK']) for r in rows]
print(f'\nconfidence={confs} k={min(ks)}..{max(ks)}')
print('extraction_log.jsonl entries:', sum(1 for _ in open('work/extraction_log.jsonl', encoding='utf-8')))
