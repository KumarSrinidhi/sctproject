"""Phase 2 independent verification (Test Designer pass).

Derived from the approved Phase 2 specification (task checklist) + work/audit_phase2_inputs.json
+ the Phase 1 backups — NOT from the apply implementation. Each check states its oracle.

Writes work/phase2_verification.json; exit 0 only if every check passes.
"""
import json, csv, hashlib, sys, collections
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path('work'); OUT = Path('.')
inp = json.load(open(BASE / 'audit_phase2_inputs.json', encoding='utf-8'))
p1 = json.load(open(BASE / 'phase2_source_hashes_before.json'))  # pre-apply source-doc snapshot
changes = json.load(open(BASE / 'phase2_applied_changes.json', encoding='utf-8'))

drops = set(inp['drop_intra_recommended'] + inp['drop_cross_recommended']
            + inp['drop_out_of_scope_recommended'])
title_fixes = inp['title_fixes']

def read_csv(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

ds = read_csv(OUT / 'thermal_conductivity_dataset.csv')
inv = read_csv(OUT / 'paper_inventory.csv')
log = read_csv(OUT / 'extraction_log.csv')
unc = read_csv(OUT / 'uncertain_measurements.csv')
rows = [json.loads(l) for l in open(BASE / 'rows_raw.jsonl', encoding='utf-8')]
nlog = [json.loads(l) for l in open(BASE / 'extraction_log.jsonl', encoding='utf-8')]
bak_ds = read_csv(BASE / 'backup_phase1' / 'thermal_conductivity_dataset.csv')
bak_rows = [json.loads(l) for l in open(BASE / 'backup_phase1' / 'rows_raw.jsonl', encoding='utf-8')]
bak_log = read_csv(BASE / 'backup_phase1' / 'extraction_log.csv')

by_id = {r['row_id']: r for r in ds}
bak_conf = collections.Counter(r['confidence'] for r in bak_rows)
drop_conf = collections.Counter(by_id and next(r for r in bak_rows if r['row_id'] == d)['confidence']
                                for d in drops)

results = []
def check(cid, desc, ok, detail=''):
    results.append({'id': cid, 'description': desc, 'status': 'PASS' if ok else 'FAIL',
                    'detail': str(detail)})
    print(f'[{"PASS" if ok else "FAIL"}] {cid}: {desc}' + (f' — {detail}' if detail else ''))

# 1. row count == 173 (dataset CSV and rows_raw.jsonl)
check('row_count', 'Dataset has exactly 173 rows (CSV and rows_raw.jsonl)',
      len(ds) == 173 and len(rows) == 173, f'csv={len(ds)} jsonl={len(rows)}')

# 2. no duplicate row_ids
ids = [r['row_id'] for r in ds]
check('unique_row_ids', 'No duplicate row_ids; CSV/JSONL id sets identical',
      len(set(ids)) == len(ids) and set(ids) == {r['row_id'] for r in rows},
      f'unique={len(set(ids))}')

# 3. no dropped rows remain anywhere
leftover = (set(ids) | {r['row_id'] for r in rows}) & drops
check('drops_removed', 'None of the 15 drop-list row_ids remain in dataset or rows_raw.jsonl',
      not leftover, f'leftover={sorted(leftover) or "none"}')

# 4. titles corrected (11 DOIs, spot-check 3) — oracle: audit JSON corrected strings;
#    old titles must be absent from dataset, inventory AND extraction_log
old_any = []
for doi, tf in title_fixes.items():
    for r in ds:
        if r['doi'] == doi and r['paper_title'] != tf['corrected']:
            old_any.append((r['row_id'], 'dataset'))
    for name, tbl, col in [('inventory', inv, 'paper_title'), ('log', log, 'paper_title')]:
        for row in tbl:
            if row.get('doi') == doi and row.get(col) != tf['corrected']:
                old_any.append((doi, name))
for doi, tf in title_fixes.items():
    for row in inv + log:
        if row.get('paper_title') == tf['current']:
            old_any.append((doi, 'stale-old-title'))
stale_old = [(d, tf['current'][:40]) for d, tf in title_fixes.items()
             if any(r.get('paper_title') == tf['current'] for r in ds + inv + log)]
check('titles_corrected', 'All 11 DOIs carry corrected paper_title in dataset, inventory and extraction_log; no old title remains',
      not old_any and not stale_old, f'violations={old_any[:5]} stale={stale_old[:5]}')
spot = ['10.3390/polym11121990', '10.1039/c8ra10211b', '10.3390/nano8120997']
spot_ok = all(all(r['paper_title'] == title_fixes[d]['corrected'] for r in ds if r['doi'] == d)
              for d in spot)
check('titles_spotcheck', 'Spot-check 3 corrected titles (polym11121990, c8ra10211b, nano8120997)',
      spot_ok, '; '.join(spot))

# 5. loading fixes: every listed row is either dropped or carries the corrected value
bad_load, applied, skipped = [], [], []
for lf in inp['loading_fixes']:
    rid = lf['row_id']
    if rid not in by_id:
        if rid not in drops:
            bad_load.append((rid, 'absent but not in drop list'))
        else:
            skipped.append(rid)
        continue
    r = by_id[rid]
    applied.append(rid)
    if str(r['filler_loading_wt_pct']) != str(float(lf['corrected_wt_pct'])):
        bad_load.append((rid, f"wt={r['filler_loading_wt_pct']} != {lf['corrected_wt_pct']}"))
    if str(r['filler_loading_original_value']) != str(float(lf['corrected_wt_pct'])):
        bad_load.append((rid, f"orig={r['filler_loading_original_value']} != {lf['corrected_wt_pct']}"))
    if 'Loading corrected in Phase 2 audit (Table 1 weight composition)' not in r['notes']:
        bad_load.append((rid, 'required note missing'))
check('loadings_corrected', 'All 20 listed loadings: applied-with-corrected-value or dropped-row (3 expected skipped)',
      not bad_load and len(applied) == 17 and len(skipped) == 3,
      f'applied={len(applied)} skipped={skipped} bad={bad_load[:5]}')
etl70 = [r['row_id'] for r in ds if str(r['filler_loading_wt_pct']) == '58.0'
         and r['doi'] == '10.3390/polym13060955']
check('loading_spotcheck_ETL70', 'Spot-check: ETL-70 grade rows now 58.0 wt%',
      len(etl70) >= 1, f'rows={etl70}')

# 6. k range unchanged
ks = [float(r['k_composite_W_mK']) for r in ds]
check('k_range', 'k range still 0.17–19.0 W/m·K',
      min(ks) == 0.17 and max(ks) == 19.0, f'{min(ks)}..{max(ks)}')

# 7. confidence labels High/Medium only, counts = original minus dropped
conf = collections.Counter(r['confidence'] for r in ds)
exp_high = bak_conf['High'] - drop_conf['High']
exp_med = bak_conf['Medium'] - drop_conf['Medium']
check('confidence_labels', 'Only High/Medium labels; counts = pre-apply counts minus dropped rows',
      set(conf) <= {'High', 'Medium'} and conf['High'] == exp_high and conf['Medium'] == exp_med,
      f'got H={conf["High"]}/M={conf["Medium"]}, expected H={exp_high}/M={exp_med}')

# 8. Medium rows == uncertain_measurements.csv
med_ids = {r['row_id'] for r in ds if r['confidence'] == 'Medium'}
unc_ids = {r['row_id'] for r in unc}
check('medium_subset_uncertain', 'Medium-confidence rows exactly covered by uncertain_measurements.csv',
      med_ids <= unc_ids and unc_ids <= med_ids, f'medium={sorted(med_ids)} unc={sorted(unc_ids)}')

# 9. inventory per-DOI counts == dataset counts (plus DOI sets and k ranges)
ds_counts = collections.Counter(r['doi'] for r in ds)
inv_counts = {r['doi']: int(r['rows_extracted']) for r in inv}
inv_ok = dict(ds_counts) == inv_counts and len(inv) == len(ds_counts)
for r in inv:
    ks_d = [float(x['k_composite_W_mK']) for x in ds if x['doi'] == r['doi']]
    if float(r['k_min_W_mK']) != min(ks_d) or float(r['k_max_W_mK']) != max(ks_d):
        inv_ok = False
check('inventory_consistent', 'paper_inventory per-DOI row counts and k min/max match dataset; DOI sets equal',
      inv_ok, f'dois={len(ds_counts)}')

# 10. protected source docs unchanged (pre-apply snapshot)
bad_src = [p for p, h in p1.items()
           if hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
check('source_docs_unchanged', f'All {len(p1)} protected source docs (fulltext/, extract_*.py, io_append.py, build_deliverables.py) unchanged',
      not bad_src, f'changed={bad_src}')

# 11. unusable_sources.csv untouched vs Phase 1 baseline
h = hashlib.sha256((OUT / 'unusable_sources.csv').read_bytes()).hexdigest()[:16]
check('unusable_unchanged', 'unusable_sources.csv matches Phase 1 baseline hash (48 entries)',
      h == inp['baseline_hashes']['unusable_sources.csv'], h)

# 12. backups exist (both naming schemes) for the 6 mandated files
need = ['thermal_conductivity_dataset.csv', 'paper_inventory.csv', 'extraction_log.csv',
        'uncertain_measurements.csv']
bk_ok = all((BASE / f'backup_phase1_{f}').exists() and (BASE / 'backup_phase1' / f).exists()
            for f in need) \
    and (BASE / 'backup_phase1_rows_raw.jsonl').exists() \
    and (BASE / 'backup_phase1_extraction_log.jsonl').exists()
check('backups_exist', 'Backups exist for the 6 mandated files (prefix + directory schemes)',
      bk_ok)

# 13. extraction log: 71 entries, prior 70 preserved, PHASE2-REMEDIATION entry well-formed
p2 = [e for e in log if e['candidate_id'] == 'PHASE2-REMEDIATION']
old_pres = [e['candidate_id'] for e in bak_log] == [e['candidate_id'] for e in log[:70]]
# prior entries preserved except intended title corrections
title_ok_prior = True
for i, (b, a) in enumerate(zip(bak_log, log[:70])):
    for k in b:
        if b[k] != a.get(k):
            if k == 'paper_title' and b['doi'] in title_fixes and b[k] == title_fixes[b['doi']]['current']:
                continue  # intended title overwrite
            title_ok_prior = False
log_ok = (len(log) == 71 and len(nlog) == 71 and old_pres and len(p2) == 1
          and p2[0]['rows_appended'] == '0' and 'rows_removed=15' in p2[0]['qc_findings'])
check('extraction_log', 'extraction_log: 71 entries, prior 70 preserved (only sanctioned title fixes), PHASE2-REMEDIATION rows_appended=0 rows_removed=15',
      log_ok and title_ok_prior,
      f'entries={len(log)} p2={len(p2)} prior_preserved={old_pres} prior_only_title_diffs={title_ok_prior}')

# 14. schema + encoding preserved
hdr_ok = (list(ds[0].keys()) == list(bak_ds[0].keys()) and len(ds[0]) == 31
          and (OUT / 'thermal_conductivity_dataset.csv').read_bytes()[:3] == b'\xef\xbb\xbf'
          and (OUT / 'uncertain_measurements.csv').read_bytes()[:3] == b'\xef\xbb\xbf'
          and (OUT / 'paper_inventory.csv').read_bytes()[:3] == b'\xef\xbb\xbf'
          and (OUT / 'extraction_log.csv').read_bytes()[:3] == b'\xef\xbb\xbf')
check('schema_encoding', 'All four CSVs: 31-col dataset schema unchanged, utf-8-sig BOM present',
      hdr_ok, f'cols={len(ds[0])}')

# 15. rows_raw.jsonl content == dataset CSV content
mismatch = []
jmap = {r['row_id']: r for r in rows}
for r in ds:
    j = jmap.get(r['row_id'])
    if j is None:
        mismatch.append((r['row_id'], 'missing in jsonl')); continue
    for c in r:
        if str(j.get(c, '')) != str(r[c]):
            mismatch.append((r['row_id'], c, j.get(c), r[c])); break
check('jsonl_csv_consistent', 'rows_raw.jsonl matches deliverable CSV row-for-row (all 31 fields)',
      not mismatch and len(jmap) == len(ds), f'mismatch={mismatch[:3]}')

# 16. the 9 non-numeric cells are clean; original strings preserved in notes
nc_bad = []
for nv in inp['numeric_col_violations']:
    v = by_id[nv['row_id']][nv['column']]
    if v not in ('',) :
        try: float(v)
        except ValueError: nc_bad.append((nv['row_id'], v))
    if nv['value'] not in by_id[nv['row_id']]['notes']:
        nc_bad.append((nv['row_id'], 'orig string not in notes'))
for u in inp['unparsable_original_strings']:
    v = by_id[u['row_id']]['filler_loading_original_value']
    try:
        if v != '': float(v)
    except ValueError:
        nc_bad.append((u['row_id'], v))
    if u['value'] not in by_id[u['row_id']]['notes']:
        nc_bad.append((u['row_id'], 'orig string not in notes'))
check('non_numeric_repaired', '9 audited non-numeric cells now empty/parseable; originals relocated to notes',
      not nc_bad, f'bad={nc_bad}')

# 17. sample-label repairs (expectations from Phase 1 findings + README hybrid convention)
lab = {s: next(r for r in ds if r['row_id'].endswith('-' + s)) for s in ['036', '147', '180', '095', '152', '153', '188']}
lab_ok = ('hybrid' in lab['036']['filler_material'] and 'Cu' in lab['036']['filler_material']
          and lab['147']['filler_material'] in ('none', 'neat')
          and 'Al2O3' in lab['180']['filler_material'] and 'BN' in lab['180']['filler_material']
          and lab['180']['filler_material'] != 'AlN'
          and all('hybrid' in lab[s]['filler_material'] for s in ['095', '152', '153', '188'])
          and not any(r['row_id'].endswith('-151') for r in ds))
check('label_repairs', 'Sample labels: 036 hybrid (Cu/BN), 147 none, 180 Al2O3/BN (not AlN); 095/152/153/188 contain "hybrid"; 151 dropped',
      lab_ok, '; '.join(f'{s}={lab[s]["filler_material"]}' for s in lab))

# 18. README / QC report counts updated and consistent with the dataset
readme = (OUT / 'README.md').read_text(encoding='utf-8')
qcr = (OUT / 'quality_control_report.md').read_text(encoding='utf-8')
n = len(ds); npap = len(ds_counts); nmed = conf['Medium']; nhigh = conf['High']
doc_ok = (f'{n} rows / {npap} papers' in readme
          and f'({len(log)} entries)' in readme
          and f'{nmed} Medium-confidence rows' in readme
          and '| Total rows | 173 |' in qcr
          and f'| Unique papers | {npap} |' in qcr
          and f'| High | {nhigh} (' in qcr
          and f'| Medium | {nmed} (' in qcr
          and '## 8. Phase 2 remediation' in qcr
          and '| Total rows | 188 |' not in qcr)
check('docs_updated', 'README + QC report counts updated (173 rows, 63 papers, 71 log entries, Medium count) and Phase 2 section present',
      doc_ok)

# 19. applied-changes record consistent with the plan
chg_ok = (changes['drops']['total'] == 15
          and changes['loading_fixes']['listed'] == 20
          and len(changes['loading_fixes']['applied']) + len(changes['loading_fixes']['skipped_dropped']) == 20
          and changes['title_overwrites']['dois'] == 11
          and len(changes['non_numeric_repairs']['numeric_column_cells']) == 2
          and len(changes['non_numeric_repairs']['text_column_cells']) == 7
          and changes['after']['rows'] == 173
          and changes['extraction_log_entry']['rows_removed'] == 15)
check('changes_record', 'work/phase2_applied_changes.json matches approved plan counts (15/20/11/3/9, after=173)',
      chg_ok)

# 20. backups byte-match the Phase 1 baseline (restore path is sound)
bak_ok = True
for name, hsh in inp['baseline_hashes'].items():
    b = BASE / 'backup_phase1' / name
    if b.exists() and hashlib.sha256(b.read_bytes()).hexdigest()[:16] != hsh:
        bak_ok = False
check('backups_match_baseline', 'Directory backups byte-match Phase 1 baseline hashes (reversibility verified)',
      bak_ok)

n_pass = sum(1 for r in results if r['status'] == 'PASS')
n_fail = len(results) - n_pass
out = {'generated': '2026-10-14', 'overall': 'PASS' if n_fail == 0 else 'FAIL',
       'passed': n_pass, 'failed': n_fail, 'checks': results}
json.dump(out, open(BASE / 'phase2_verification.json', 'w', encoding='utf-8'), indent=2,
          ensure_ascii=False)
print(f'\nOVERALL: {out["overall"]} ({n_pass}/{len(results)} checks passed)')
sys.exit(0 if n_fail == 0 else 1)
