"""Phase 2 apply — ARGUS thermal-conductivity dataset remediation.

Reads approved change lists from work/audit_phase2_inputs.json (schema-checked; aborts if wrong),
applies them to work/rows_raw.jsonl + work/extraction_log.jsonl, regenerates the four derived
CSVs byte-faithfully (proved by phase2_preflight.py), updates README.md / quality_control_report.md
counts, appends the PHASE2-REMEDIATION extraction-log entry, and records every change in
work/phase2_applied_changes.json.

Safety:
  - verifies Phase 1 baseline SHA-256 of all 7 deliverables BEFORE write
  - verifies protected source docs (fulltext/, extract_*.py, io_append.py, build_deliverables.py)
    unchanged AFTER write (hashes from phase2_preflight.py)
  - unusable_sources.csv must be unchanged (baseline from audit inputs JSON)
  - backups must exist in work/backup_phase1/ (created if missing)
Reversible via work/phase2_restore.py.
"""
import json, csv, hashlib, sys, shutil, collections
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path('work')
OUT = Path('.')

# ----------------------------------------------------------------- guards
inp = json.load(open(BASE / 'audit_phase2_inputs.json', encoding='utf-8'))
REQUIRED = ['baseline_hashes', 'title_fixes', 'loading_fixes', 'drop_intra_recommended',
            'drop_cross_recommended', 'drop_out_of_scope_recommended',
            'numeric_col_violations', 'unparsable_original_strings', 'row_totals']
missing = [k for k in REQUIRED if k not in inp]
if missing:
    print(f'FATAL: audit_phase2_inputs.json missing keys: {missing} — STOPPING, not guessing.')
    sys.exit(2)

def sha16(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]

# baseline check BEFORE write (all 7 deliverables must match Phase 1)
for name, h in inp['baseline_hashes'].items():
    got = sha16(OUT / name)
    if got != h:
        print(f'FATAL: baseline mismatch BEFORE write: {name} expected {h} got {got}')
        sys.exit(3)
print(f'baseline before write: {len(inp["baseline_hashes"])} deliverables OK')

# backups must exist
BACKUP_DIR = BASE / 'backup_phase1'
BACKUP_DIR.mkdir(exist_ok=True)
backups = ['thermal_conductivity_dataset.csv', 'paper_inventory.csv', 'extraction_log.csv',
           'uncertain_measurements.csv', 'unusable_sources.csv', 'quality_control_report.md',
           'README.md']
for f in backups:
    for p in [OUT / f, BACKUP_DIR / f, BASE / f'backup_phase1_{f}']:
        if not p.exists():
            shutil.copy2(OUT / f, p)
            print(f'backup created: {p}')
for f in ['rows_raw.jsonl', 'extraction_log.jsonl']:
    for p in [BASE / f'backup_phase1_{f}', BACKUP_DIR / f]:
        if not p.exists():
            shutil.copy2(BASE / f, p)
            print(f'backup created: {p}')
print('backups present')

# ----------------------------------------------------------------- load
rows = [json.loads(l) for l in open(BASE / 'rows_raw.jsonl', encoding='utf-8')]
log = [json.loads(l) for l in open(BASE / 'extraction_log.jsonl', encoding='utf-8')]
assert (BASE / 'rows_raw.jsonl').read_bytes().endswith(b'\r\n'), 'rows_raw.jsonl CRLF expected'
assert (BASE / 'extraction_log.jsonl').read_bytes().endswith(b'\r\n'), 'extraction_log.jsonl CRLF expected'
by_id = {r['row_id']: r for r in rows}
n_before = len(rows)
assert n_before == inp['row_totals']['current'] == 188, f'unexpected starting row count {n_before}'

changes = {'applied_at': '2026-10-14',
           'input': 'work/audit_phase2_inputs.json',
           'backup_dir': 'work/backup_phase1/',
           'backup_prefix': 'work/backup_phase1_',
           'before': {'rows': n_before}}

# ----------------------------------------------------------------- 1. drops (15)
drops = (inp['drop_intra_recommended'] + inp['drop_cross_recommended']
         + inp['drop_out_of_scope_recommended'])
assert len(drops) == len(set(drops)) == 15, f'expected 15 unique drops, got {len(drops)}'
dropped_ids = [r['row_id'] for r in rows if r['row_id'] in set(drops)]
assert len(dropped_ids) == 15, f'drop rows not all found: missing {set(drops) - set(dropped_ids)}'
rows = [r for r in rows if r['row_id'] not in set(drops)]
by_id = {r['row_id']: r for r in rows}
changes['drops'] = {'total': 15,
                    'intra_paper_duplicates': inp['drop_intra_recommended'],
                    'cross_paper_duplicates': inp['drop_cross_recommended'],
                    'out_of_scope': inp['drop_out_of_scope_recommended'],
                    'row_ids_dropped': dropped_ids}
print(f'dropped 15 rows -> {len(rows)}')

# ----------------------------------------------------------------- 2. titles (11 DOIs)
title_rows, title_log_entries, title_skipped = [], [], []
for doi, tf in inp['title_fixes'].items():
    hit = [r for r in rows if r['doi'] == doi]
    assert hit, f'title-fix DOI {doi} has no surviving rows'
    for r in hit:
        if r['paper_title'] == tf['current']:
            r['paper_title'] = tf['corrected']
            title_rows.append(r['row_id'])
        elif r['paper_title'] == tf['corrected']:
            title_skipped.append(r['row_id'])  # already correct (impossible pre-apply, defensive)
        else:
            raise AssertionError(f'{doi} row {r["row_id"]} has unexpected title {r["paper_title"]!r}')
for e in log:
    doi = e.get('doi')
    if doi in inp['title_fixes'] and e.get('paper_title') == inp['title_fixes'][doi]['current']:
        e['paper_title'] = inp['title_fixes'][doi]['corrected']
        title_log_entries.append(e.get('candidate_id'))
changes['title_overwrites'] = {'dois': len(inp['title_fixes']),
                               'dataset_rows_fixed': title_rows,
                               'already_correct_skipped': title_skipped,
                               'extraction_log_entries_fixed': title_log_entries}
print(f'titles: {len(inp["title_fixes"])} DOIs, {len(title_rows)} dataset rows, '
      f'{len(title_log_entries)} log entries')

# ----------------------------------------------------------------- 3. loading fixes (20)
load_applied, load_skipped = [], []
for lf in inp['loading_fixes']:
    rid = lf['row_id']
    if rid not in by_id:
        assert rid in set(drops), f'loading-fix row {rid} missing but not in drop list'
        load_skipped.append(rid)
        continue
    r = by_id[rid]
    assert str(r['filler_loading_wt_pct']) == lf['stored_wt_pct'], \
        f'{rid}: stored wt {r["filler_loading_wt_pct"]} != expected {lf["stored_wt_pct"]}'
    r['filler_loading_wt_pct'] = float(lf['corrected_wt_pct'])
    r['filler_loading_original_value'] = float(lf['corrected_wt_pct'])
    r['filler_loading_original_unit'] = 'wt%'
    note = 'Loading corrected in Phase 2 audit (Table 1 weight composition).'
    if note not in r['notes']:
        r['notes'] = (r['notes'].rstrip() + ' ' + note).strip()
    load_applied.append(rid)
changes['loading_fixes'] = {'listed': 20, 'applied': load_applied, 'skipped_dropped': load_skipped,
                            'note_added': 'Loading corrected in Phase 2 audit (Table 1 weight composition).',
                            'original_value_update': 'filler_loading_original_value set to corrected wt% with unit wt% (Table 1 weight basis); vol% preserved in filler_loading_vol_pct'}
print(f'loadings: {len(load_applied)} applied, {len(load_skipped)} skipped (dropped)')

# ----------------------------------------------------------------- 4. sample labels (3 + hybrid convention)
# exact corrected values per Phase 1 findings (audit_phase1_rows.json, report D6/10.5) and
# README hybrid convention ("filler_material contains 'hybrid'"); rows keyed by the
# suffix ids listed in audit_phase2_inputs.json::pending_decisions.
label_fixes = {
    '036': 'Cu/BN hybrid',          # (CuNPs-CuNWs)@BN/PI hybrid film mislabeled 'BN'
    '147': 'none',                  # 0 wt% baseline mislabeled 'cBN'
    '180': 'Al2O3/BN hybrid',       # trimodal Al2O3+BN mislabeled 'AlN' (0 hits in paper)
    '095': 'BNNS hybrid',           # BNNS+SiO2+CNT co-filler: hybrid convention
    '152': 'h-BN/CNT hybrid',       # h-BN+CNT co-filler: hybrid convention
    '153': 'h-BN/CNT hybrid',       # h-BN+CNT co-filler: hybrid convention
    '188': 'h-BN/CNT hybrid',       # h-BN+CNT co-filler: hybrid convention
    '151': 'h-BN/CNT hybrid',       # hybrid convention, but row 151 is dropped -> recorded skipped
}
label_applied, label_skipped, label_unresolved = {}, [], []
for suf, newval in label_fixes.items():
    matches = [rid for rid in by_id if rid.endswith('-' + suf)]
    if not matches:
        # dropped row: expected only for 151
        assert suf in {d.split('-')[-1] for d in drops}, f'label row suffix {suf} not found and not a drop'
        label_skipped.append(f'{suf} (dropped in Phase 2)')
        continue
    assert len(matches) == 1, f'ambiguous label suffix {suf}: {matches}'
    rid = matches[0]
    r = by_id[rid]
    old = r['filler_material']
    r['filler_material'] = newval
    label_applied[rid] = {'old': old, 'new': newval}
changes['sample_label_repairs'] = {'applied': label_applied, 'skipped': label_skipped,
                                   'basis': 'audit_phase1_rows.json findings + README hybrid convention (filler_material contains "hybrid"); filler_material_original values verified verbatim-correct and left unchanged'}
print(f'labels: {len(label_applied)} applied, {len(label_skipped)} skipped')

# ----------------------------------------------------------------- 5. non-numeric repairs (9)
num_fixes = []
for nv in inp['numeric_col_violations']:
    rid, col = nv['row_id'], nv['column']
    r = by_id[rid]
    assert str(r[col]) == nv['value'], f'{rid}.{col} = {r[col]!r} != audited {nv["value"]!r}'
    note = f'{col} non-numeric value {nv["value"]!r} relocated to notes in Phase 2 audit.'
    r[col] = ''
    r['notes'] = (r['notes'].rstrip() + ' ' + note).strip()
    num_fixes.append({'row_id': rid, 'column': col, 'old': nv['value'], 'new': '',
                      'note': note})
txt_fixes = []
for u in inp['unparsable_original_strings']:
    rid = u['row_id']
    r = by_id[rid]
    assert str(r['filler_loading_original_value']) == u['value'], \
        f'{rid} orig value {r["filler_loading_original_value"]!r} != audited {u["value"]!r}'
    newval = u['numeric_wt'] or u['numeric_vol'] or ''
    old = r['filler_loading_original_value']
    r['filler_loading_original_value'] = float(newval) if newval else ''
    note = (f"filler_loading_original_value string {old!r} relocated to notes in Phase 2 audit; "
            f"field set to {newval if newval else 'empty'} per audit guidance.")
    r['notes'] = (r['notes'].rstrip() + ' ' + note).strip()
    # sanity: wt/vol columns must already equal the audit guidance
    if u['numeric_wt']:
        assert str(r['filler_loading_wt_pct']) == u['numeric_wt'], f'{rid} wt mismatch'
    if u['numeric_vol']:
        assert str(r['filler_loading_vol_pct']) == u['numeric_vol'], f'{rid} vol mismatch'
    txt_fixes.append({'row_id': rid, 'old': old, 'new': r['filler_loading_original_value'],
                      'note': note})
changes['non_numeric_repairs'] = {'numeric_column_cells': num_fixes,
                                  'text_column_cells': txt_fixes}
print(f'non-numeric: {len(num_fixes)} numeric-col + {len(txt_fixes)} text-col repaired')

# ----------------------------------------------------------------- assert final row count
assert len(rows) == 173 == inp['row_totals']['after_all_recommended'], \
    f'expected 173 rows, got {len(rows)}'
changes['after'] = {'rows': len(rows),
                    'papers': len({r['doi'] for r in rows})}

# ----------------------------------------------------------------- 6. extraction-log entry
qc_text = ('rows_removed=15 (9 intra-paper duplicate rows; 5 cross-paper duplicate rows; '
           '1 out-of-scope literature-quote row 4a11b03c-151); '
           'loading corrections: 20 rows listed in audit_phase2_inputs.json, 17 applied to '
           'surviving rows, 3 skipped (row dropped as cross-paper duplicate); '
           'paper_title overwritten for 11 DOIs (dataset + inventory + this log); '
           'sample-label repairs: 3 (rows 036/147/180) + 4 hybrid-convention labels (095/152/153/188); '
           'non-numeric repairs: 2 numeric-column cells (094/130) + 7 text-column loading strings; '
           'dataset 188 -> 173 rows, 63 papers')
entry = {'candidate_id': 'PHASE2-REMEDIATION', 'doi': '',
         'paper_title': 'Phase 2 audit remediation (dataset-wide, no new source extraction)',
         'date_processed': '2026-10-14',
         'access_result': 'n/a (metadata remediation from Phase 1 audit; no new source access)',
         'files_inspected': 'work/audit_phase2_inputs.json; audit_phase1_report.md',
         'tables_inspected': '', 'figures_inspected': '', 'candidate_measurements': 0,
         'rows_appended': 0, 'unit_conversions': 'none',
         'duplicate_checks': '9 intra-paper + 5 cross-paper duplicate rows removed',
         'qc_findings': qc_text, 'rows_rejected_at_append': [],
         'rows_removed': 15,
         'notes': 'Phase 2 remediation: 15 drops, 20 loading fixes (17 applied), 11 title overwrites, '
                  '3 sample-label repairs + 4 hybrid-convention labels, 9 non-numeric cell repairs; '
                  'derived deliverables regenerated; reversible from work/backup_phase1/'}
assert not any(e.get('candidate_id') == 'PHASE2-REMEDIATION' for e in log), 'entry already present'
log.append(entry)
changes['extraction_log_entry'] = {'candidate_id': 'PHASE2-REMEDIATION',
                                   'rows_appended': 0, 'rows_removed': 15,
                                   'entries_before': 70, 'entries_after': len(log)}
print(f'extraction log: {len(log)} entries')

# ----------------------------------------------------------------- write JSONL (CRLF, raw UTF-8)
def write_jsonl(path, items):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\r\n'.join(json.dumps(x, ensure_ascii=False) for x in items) + '\r\n')

write_jsonl(BASE / 'rows_raw.jsonl', rows)
write_jsonl(BASE / 'extraction_log.jsonl', log)
print('JSONL written: rows_raw.jsonl=173, extraction_log.jsonl=71')

# ----------------------------------------------------------------- regenerate CSVs
COLS = ['row_id', 'doi', 'source_url', 'paper_title', 'year', 'matrix_polymer', 'curing_agent',
        'filler_material', 'filler_material_original', 'filler_shape', 'filler_aspect_ratio',
        'filler_mean_size_um', 'size_distribution', 'filler_loading_vol_pct', 'filler_loading_wt_pct',
        'filler_loading_original_value', 'filler_loading_original_unit', 'functionalization',
        'filler_alignment', 'processing_method', 'k_matrix_W_mK', 'k_composite_W_mK', 'k_direction',
        'measurement_method', 'measurement_temperature_C', 'k_original_value', 'k_original_unit',
        'value_source', 'source_location', 'confidence', 'notes']

with open(OUT / 'thermal_conductivity_dataset.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
    for r in rows: w.writerow(r)

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
with open(OUT / 'paper_inventory.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=inv_cols); w.writeheader()
    for d in sorted(papers, key=lambda x: papers[x]['doi']):
        p = papers[d]
        w.writerow({'doi': p['doi'], 'paper_title': p['paper_title'], 'year': p['year'],
                    'source_url': p['source_url'], 'rows_extracted': p['rows_extracted'],
                    'filler_materials': '; '.join(sorted(p['filler_materials'])),
                    'matrix_polymers': '; '.join(sorted(p['matrix_polymers'])),
                    'k_min_W_mK': p['k_min'], 'k_max_W_mK': p['k_max']})

log_cols = ['candidate_id','doi','paper_title','date_processed','access_result','files_inspected',
            'tables_inspected','figures_inspected','candidate_measurements','rows_appended',
            'unit_conversions','duplicate_checks','qc_findings','rows_rejected_at_append']
with open(OUT / 'extraction_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=log_cols, extrasaction='ignore'); w.writeheader()
    for e in log:
        row = {c: e.get(c, '') for c in log_cols}
        rej = e.get('rows_rejected_at_append', [])
        if rej:
            row['rows_rejected_at_append'] = '; '.join(f'{rid}:{reason}' for rid, reason in rej)
        w.writerow(row)

uncertain = [r for r in rows if r['confidence'] != 'High']
with open(OUT / 'uncertain_measurements.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
    for r in uncertain: w.writerow(r)
print(f'regenerated: dataset=173, inventory={len(papers)} papers, log=71, uncertain={len(uncertain)}')

# ----------------------------------------------------------------- stats for docs
by_matrix = collections.Counter()
for r in rows:
    m = r['matrix_polymer']
    if 'epoxy' in m.lower() or 'dgeba' in m.lower() or 'emc' in m.lower() or 'ep ' in m.lower():
        by_matrix['epoxy-based'] += 1
    elif 'polyimide' in m.lower() or 'pi' == m.lower().strip():
        by_matrix['polyimide'] += 1
    elif 'silicone' in m.lower():
        by_matrix['silicone'] += 1
    elif 'peg' in m.lower():
        by_matrix['PEG PCM'] += 1
    elif 'polyurethane' in m.lower() or 'pu' == m.lower().strip():
        by_matrix['polyurethane'] += 1
    elif 'polystyrene' in m.lower() or 'ps' == m.lower().strip():
        by_matrix['polystyrene'] += 1
    elif 'liquid crystal' in m.lower() or 'lc' in m.lower():
        by_matrix['liquid crystal epoxy'] += 1
    else:
        by_matrix[m[:30]] += 1
by_filler = collections.Counter(r['filler_material'] for r in rows)
by_conf = collections.Counter(r['confidence'] for r in rows)
by_source = collections.Counter(r['value_source'] for r in rows)
k_vals = sorted(float(r['k_composite_W_mK']) for r in rows)
years = sorted(int(r['year']) for r in rows if r['year'])
kmin, kmax = k_vals[0], k_vals[-1]
median = k_vals[len(k_vals) // 2]
n = len(rows); n_papers = len(papers)
n_high, n_med = by_conf['High'], by_conf['Medium']
pct = lambda c: f'{100 * c / n:.1f}%'
print(f'stats: rows={n} papers={n_papers} conf={n_high}/{n_med} k={kmin}..{kmax} med={median} '
      f'years={years[0]}..{years[-1]}')

# ----------------------------------------------------------------- README.md
readme = (OUT / 'README.md').read_text(encoding='utf-8')
readme_repl = [
    ('| `thermal_conductivity_dataset.csv` | 188 rows / 63 papers, 31 columns (full schema) |',
     f'| `thermal_conductivity_dataset.csv` | {n} rows / {n_papers} papers, 31 columns (full schema) |'),
    ('| `paper_inventory.csv` | 63 papers with row counts, fillers, matrices, k ranges |',
     f'| `paper_inventory.csv` | {n_papers} papers with row counts, fillers, matrices, k ranges |'),
    ('| `extraction_log.csv` | Per-batch audit trail (70 entries) with tables/figures inspected |',
     f'| `extraction_log.csv` | Per-batch audit trail ({len(log)} entries) with tables/figures inspected |'),
    ('| `uncertain_measurements.csv` | 9 Medium-confidence rows (flagged for review) |',
     f'| `uncertain_measurements.csv` | {n_med} Medium-confidence rows (flagged for review) |'),
    (f'**Primary (epoxy + BN/AlN):** 158 epoxy-based rows; h-BN (61) + BN (45) + BNNS (43) + AlN (22) = 171 BN/AlN-family rows.',
     f'**Primary (epoxy + BN/AlN):** {by_matrix["epoxy-based"]} epoxy-based rows; h-BN ({by_filler["h-BN"]}) + BN ({by_filler["BN"]}) + BNNS ({by_filler["BNNS"]}) + AlN ({by_filler["AlN"]}) = {by_filler["h-BN"] + by_filler["BN"] + by_filler["BNNS"] + by_filler["AlN"]} BN/AlN-family rows.'),
    ('**Optional matrices (tagged in notes):** silicone rubber (14), polyimide (9), PDMS (2), PEG PCM (2), polystyrene (2), polyurethane (1), liquid crystal epoxy (included in epoxy-based count).',
     f'**Optional matrices (tagged in notes):** silicone rubber ({by_matrix["silicone"]}), polyimide ({by_matrix["polyimide"]}), PDMS ({by_matrix["PDMS"]}), PEG PCM ({by_matrix["PEG PCM"]}), polystyrene ({by_matrix["polystyrene"]}), polyurethane ({by_matrix["polyurethane"]}), liquid crystal epoxy (included in epoxy-based count).'),
    ('- **k range:** 0.17 – 19.0 W/m·K (median 1.052)',
     f'- **k range:** {kmin} – {kmax} W/m·K (median {median})'),
    ('- **Year range:** 1997 – 2026',
     f'- **Year range:** {years[0]} – {years[-1]}'),
]
for old, new in readme_repl:
    assert old in readme, f'README anchor not found: {old[:70]!r}'
    readme = readme.replace(old, new, 1)
(OUT / 'README.md').write_text(readme, encoding='utf-8')
print('README.md updated')

# ----------------------------------------------------------------- quality_control_report.md
qc = (OUT / 'quality_control_report.md').read_text(encoding='utf-8')

def replace_block(text, start, end, new):
    i = text.index(start); j = text.index(end, i)
    return text[:i] + new + text[j:]

# summary table
qc_pairs = [
    ('| Total rows | 188 |', f'| Total rows | {n} |'),
    ('| Unique papers | 63 |', f'| Unique papers | {n_papers} |'),
    ('| Year range | 1997–2026 |', f'| Year range | {years[0]}–{years[-1]} |'),
    ('| k_composite range | 0.17 – 19.0 W/m·K |', f'| k_composite range | {kmin} – {kmax} W/m·K |'),
    ('| Median k | 1.052 W/m·K |', f'| Median k | {median} W/m·K |'),
    ('**Generated:** 2026-10-13', '**Generated:** 2026-10-13 (Phase 2 remediation applied 2026-10-14)'),
    ('## 2. Validation checks (all passed)', '## 2. Validation checks'),
    ('- **k_composite_W_mK:** all 188 values numeric, positive, in range 0.17–19.0 (no zeros, no negatives, no NaN).',
     f'- **k_composite_W_mK:** all {n} values numeric, positive, in range {kmin}–{kmax} (no zeros, no negatives, no NaN).'),
    ('- **filler_loading:** vol_pct, wt_pct, or original_value present for all rows (validation rule: at least one).',
     f'- **filler_loading:** vol_pct, wt_pct, or original_value present for {n - 1}/{n} rows (validation rule: at least one); one documented exception `bf4f3fd7-182` whose loading is the BN/PA66 sample designation `30-4` (not wt%) — string relocated to `notes` in Phase 2, no numeric loading exists for this scaffold sample.'),
    ('9 rows marked Medium confidence (listed in `uncertain_measurements.csv`). Typical reasons:',
     f'{n_med} rows marked Medium confidence (listed in `uncertain_measurements.csv`). Typical reasons:'),
    ("1. Filter `confidence == 'High'` for primary analysis (179 rows).",
     f"1. Filter `confidence == 'High'` for primary analysis ({n_high} rows)."),
    (f'2. Epoxy + BN-family subset (h-BN + BN + BNNS = 149 rows) is the core target scope.',
     f'2. Epoxy + BN-family subset (h-BN + BN + BNNS = {by_filler["h-BN"] + by_filler["BN"] + by_filler["BNNS"]} rows) is the core target scope.'),
    ('3. Optional matrices (silicone, PI, PDMS, PEG, PS, PU, LC epoxy = 30 rows) are tagged; filter out if strictly epoxy-only is needed.',
     f'3. Optional matrices (silicone, PI, PDMS, PEG, PS, PU, LC epoxy = {n - by_matrix["epoxy-based"]} rows) are tagged; filter out if strictly epoxy-only is needed.'),
]
for old, new in qc_pairs:
    assert old in qc, f'QC anchor not found: {old[:70]!r}'
    qc = qc.replace(old, new, 1)

# stats tables block (By matrix ... By value source)
mat_label = {'epoxy-based': 'Epoxy-based', 'silicone': 'Silicone', 'polyimide': 'Polyimide',
             'PEG PCM': 'PEG PCM', 'polyurethane': 'Polyurethane', 'polystyrene': 'Polystyrene',
             'liquid crystal epoxy': 'Liquid crystal epoxy'}
filler_label = {'BN': 'BN (unspecified morphology)'}
src_label = {'text': 'Text', 'table': 'Table'}
tables = ['### By matrix polymer (top)\n| Matrix | Rows |\n|---|---|\n']
tables += [f'| {mat_label.get(k, k)} | {v} |\n' for k, v in by_matrix.most_common()]
tables += ['\n### By filler material\n| Filler | Rows |\n|---|---|\n']
tables += [f'| {filler_label.get(k, k)} | {v} |\n' for k, v in by_filler.most_common()]
tables += ['\n### By confidence\n| Confidence | Rows |\n|---|---|\n']
tables += [f'| {k} | {v} ({pct(v)}) |\n' for k, v in [('High', n_high), ('Medium', n_med)]]
tables += ['\n### By value source\n| Source | Rows |\n|---|---|\n']
tables += [f'| {src_label.get(k, k)} | {v} |\n' for k, v in by_source.most_common()]
qc = replace_block(qc, '### By matrix polymer (top)', '\n---\n\n## 2.', ''.join(tables))

# Phase 2 remediation section
sec8 = f'''
---

## 8. Phase 2 remediation (applied 2026-10-14)

Machine-readable record: `work/phase2_applied_changes.json`; backups: `work/backup_phase1/` (restore via `work/phase2_restore.py`).

| Category | Count | Detail |
|---|---|---|
| Rows dropped — intra-paper duplicates | 9 | validation/retry double-append bug |
| Rows dropped — cross-paper duplicates | 5 | `a9d63e6e-014/015/016` (companion-paper pressure series), `a8b6fee9-141/142` (quoted previous work) |
| Rows dropped — out-of-scope | 1 | `4a11b03c-151` literature quote (README exclusion policy) |
| Loading corrections (Table 1 weight basis) | 20 listed / 17 applied | 3 skipped (row dropped); ETL-60→47.1, ETL-70→58.0, EJ-60→53.0, EJ-65→58.2 wt% |
| `paper_title` overwrites | 11 DOIs / {len(title_rows)} surviving dataset rows / {len(title_log_entries)} log entries | Crossref-verified titles, old titles removed everywhere |
| Sample-label repairs | 3 | `036`→Cu/BN hybrid, `147`→none (0 wt% baseline), `180`→Al2O3/BN hybrid |
| Hybrid-convention labels | 4 (+1 skipped, row dropped) | `095`, `152`, `153`, `188` now contain "hybrid" in `filler_material` |
| Non-numeric cell repairs | 9 | 2 numeric-column (`RT`@094, `55 (AlN)/35 (BN)`@130 → blank + text to notes) + 7 text-column loading strings (→ notes; field set to 31.0/22.0/32.0/empty per audit guidance) |

Dataset: **188 → {n} rows**, {n_papers} papers; confidence {n_high} High / {n_med} Medium. `extraction_log.csv` entry `PHASE2-REMEDIATION` appended (rows_appended=0, rows_removed=15); prior 70 entries preserved (titles corrected in-place for the 11 affected DOIs). `unusable_sources.csv` untouched (48 entries).

Open from Phase 1, not addressed here: `normalize_k()` false process claim (D4), unverifiable k=1.052 in row `b639a9c9-159` (D7), 3 silently dropped screened papers (D10), pipeline hardening (Phase 2b). Phase 3 (source recovery / coverage expansion) not started.
'''
qc = qc.rstrip('\n') + '\n' + sec8
(OUT / 'quality_control_report.md').write_text(qc, encoding='utf-8')
print('quality_control_report.md updated')

# ----------------------------------------------------------------- post-write guards
before = json.load(open(BASE / 'phase2_source_hashes_before.json'))
bad = []
for p, h in before.items():
    if hashlib.sha256(Path(p).read_bytes()).hexdigest() != h:
        bad.append(p)
assert not bad, f'PROTECTED SOURCE DOCS CHANGED: {bad}'
print(f'protected source docs unchanged: {len(before)} files')
assert sha16(OUT / 'unusable_sources.csv') == inp['baseline_hashes']['unusable_sources.csv'], \
    'unusable_sources.csv changed!'
print('unusable_sources.csv unchanged (baseline OK)')
changed, unchanged = [], []
for name, h in inp['baseline_hashes'].items():
    (changed if sha16(OUT / name) != h else unchanged).append(name)
assert unchanged == ['unusable_sources.csv'], f'unexpected unchanged deliverables: {unchanged}'
print(f'deliverables changed as expected: {sorted(changed)}')

changes['regenerated'] = ['thermal_conductivity_dataset.csv', 'paper_inventory.csv',
                          'extraction_log.csv', 'uncertain_measurements.csv']
changes['docs_updated'] = ['README.md', 'quality_control_report.md']
changes['stats'] = {'rows': n, 'papers': n_papers, 'high': n_high, 'medium': n_med,
                    'k_min': kmin, 'k_max': kmax, 'k_median': median,
                    'year_range': [years[0], years[-1]],
                    'by_matrix': dict(by_matrix.most_common()),
                    'by_filler': dict(by_filler.most_common()),
                    'by_confidence': dict(by_conf.most_common()),
                    'by_value_source': dict(by_source.most_common())}
json.dump(changes, open(BASE / 'phase2_applied_changes.json', 'w', encoding='utf-8'),
          indent=2, ensure_ascii=False)
print('work/phase2_applied_changes.json written')
print('APPLY OK')
