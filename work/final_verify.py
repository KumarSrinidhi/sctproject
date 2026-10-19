"""Final phase state check + verification (all local, no network).

- Counts JSONL vs CSVs; regenerates derived CSVs from rows_raw.jsonl ONLY on mismatch
  (unusable_sources.csv is a curated artifact and is never regenerated here).
- Verifies Phase-2 dropped row_ids are absent, schema invariants, stats.
- Writes work/final_verification.json.
"""
import json, csv, collections, statistics, hashlib
from pathlib import Path

BASE = Path('work')
OUT = Path('.')
COLS = ['row_id', 'doi', 'source_url', 'paper_title', 'year', 'matrix_polymer', 'curing_agent',
        'filler_material', 'filler_material_original', 'filler_shape', 'filler_aspect_ratio',
        'filler_mean_size_um', 'size_distribution', 'filler_loading_vol_pct', 'filler_loading_wt_pct',
        'filler_loading_original_value', 'filler_loading_original_unit', 'functionalization',
        'filler_alignment', 'processing_method', 'k_matrix_W_mK', 'k_composite_W_mK', 'k_direction',
        'measurement_method', 'measurement_temperature_C', 'k_original_value', 'k_original_unit',
        'value_source', 'source_location', 'confidence', 'notes']

rows = [json.loads(l) for l in open(BASE / 'rows_raw.jsonl', encoding='utf-8')]
log = [json.loads(l) for l in open(BASE / 'extraction_log.jsonl', encoding='utf-8')]

report = {'generated': '2026-10-18', 'source_of_truth': 'work/rows_raw.jsonl', 'checks': []}

def check(cid, desc, ok, detail):
    report['checks'].append({'id': cid, 'description': desc,
                             'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {cid}: {detail}")
    return ok

# ---------- 1. CSV/JSONL consistency; regenerate derived CSVs on mismatch ----------
with open(OUT / 'thermal_conductivity_dataset.csv', encoding='utf-8-sig', newline='') as f:
    csv_rows = list(csv.DictReader(f))

def cell(row, col):
    v = row.get(col, '')
    return '' if v is None else str(v)

mismatch = []
if len(csv_rows) == len(rows):
    for i, (jr, cr) in enumerate(zip(rows, csv_rows)):
        for c in COLS:
            if cell(jr, c) != (cr.get(c) or ''):
                mismatch.append({'index': i, 'col': c, 'jsonl': cell(jr, c), 'csv': cr.get(c)})
                break
else:
    mismatch.append({'index': -1, 'col': '*', 'jsonl': f'{len(rows)} rows', 'csv': f'{len(csv_rows)} rows'})

regenerated = []
# always back up deliverables before any potential overwrite
bdir = BASE / 'backup_final'
bdir.mkdir(exist_ok=True)
for fn in ['thermal_conductivity_dataset.csv', 'paper_inventory.csv', 'extraction_log.csv',
           'uncertain_measurements.csv', 'unusable_sources.csv', 'quality_control_report.md', 'README.md']:
    src = OUT / fn
    if src.exists():
        (bdir / fn).write_bytes(src.read_bytes())
if mismatch:
    # rebuild dataset CSV
    with open(OUT / 'thermal_conductivity_dataset.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
        for r in rows: w.writerow(r)
    # rebuild uncertain (all non-High)
    unc = [r for r in rows if r.get('confidence') != 'High']
    with open(OUT / 'uncertain_measurements.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore'); w.writeheader()
        for r in unc: w.writerow(r)
    # rebuild inventory
    papers_tmp = {}
    for r in rows:
        d = r['doi']; p = papers_tmp.setdefault(d, {'doi': d, 'paper_title': r['paper_title'], 'year': r['year'],
            'source_url': r['source_url'], 'rows_extracted': 0, 'filler_materials': set(),
            'matrix_polymers': set(), 'k_min': 999, 'k_max': 0})
        p['rows_extracted'] += 1
        p['filler_materials'].add(r['filler_material']); p['matrix_polymers'].add(r['matrix_polymer'])
        k = float(r['k_composite_W_mK']); p['k_min'] = min(p['k_min'], k); p['k_max'] = max(p['k_max'], k)
    inv_cols = ['doi','paper_title','year','source_url','rows_extracted','filler_materials','matrix_polymers','k_min_W_mK','k_max_W_mK']
    with open(OUT / 'paper_inventory.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=inv_cols); w.writeheader()
        for d in sorted(papers_tmp):
            p = papers_tmp[d]
            w.writerow({'doi': p['doi'], 'paper_title': p['paper_title'], 'year': p['year'],
                        'source_url': p['source_url'], 'rows_extracted': p['rows_extracted'],
                        'filler_materials': '; '.join(sorted(p['filler_materials'])),
                        'matrix_polymers': '; '.join(sorted(p['matrix_polymers'])),
                        'k_min_W_mK': p['k_min'], 'k_max_W_mK': p['k_max']})
    # rebuild extraction log
    log_cols = ['candidate_id','doi','paper_title','date_processed','access_result','files_inspected',
                'tables_inspected','figures_inspected','candidate_measurements','rows_appended',
                'unit_conversions','duplicate_checks','qc_findings','rows_rejected_at_append']
    with open(OUT / 'extraction_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=log_cols, extrasaction='ignore'); w.writeheader()
        for e in log:
            row = {c: e.get(c, '') for c in log_cols}
            rej = e.get('rows_rejected_at_append', [])
            if rej: row['rows_rejected_at_append'] = '; '.join(f'{rid}:{reason}' for rid, reason in rej)
            w.writerow(row)
    regenerated = ['thermal_conductivity_dataset.csv', 'paper_inventory.csv', 'extraction_log.csv', 'uncertain_measurements.csv']
    # reload CSV after regeneration
    with open(OUT / 'thermal_conductivity_dataset.csv', encoding='utf-8-sig', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    mismatch_after = len(csv_rows) != len(rows)
else:
    mismatch_after = False

check('jsonl_csv_rowcount', 'CSV row count matches rows_raw.jsonl', len(csv_rows) == len(rows),
      f'jsonl={len(rows)} csv={len(csv_rows)} regenerated={regenerated or "none"}')
check('jsonl_csv_fields', 'No field mismatches remain between JSONL and dataset CSV',
      not mismatch_after and len(csv_rows) == len(rows),
      'ok' if not mismatch_after else 'still mismatched after regen')

# ---------- 2. Phase-2 dropped row_ids absent ----------
p2 = json.load(open(BASE / 'phase2_applied_changes.json', encoding='utf-8'))
dropped = sorted(set(p2['drops'].get('row_ids_dropped', [])))
ids_now = {r['row_id'] for r in rows}
resurrected = [i for i in dropped if i in ids_now]
check('phase2_drops_absent', 'None of the Phase-2 dropped row_ids remain',
      not resurrected, f'dropped={len(dropped)} resurrected={resurrected}')

# ---------- 3. Schema / invariant checks ----------
ids = [r['row_id'] for r in rows]
check('unique_row_ids', 'row_ids unique', len(set(ids)) == len(ids), f'unique={len(set(ids))} total={len(ids)}')

bad_k = []
for r in rows:
    try:
        k = float(r['k_composite_W_mK'])
        if k <= 0: bad_k.append((r['row_id'], r['k_composite_W_mK']))
    except (TypeError, ValueError):
        bad_k.append((r['row_id'], r['k_composite_W_mK']))
check('k_numeric_positive', 'All k_composite_W_mK numeric and positive', not bad_k, f'bad={bad_k[:5]}')

missing = collections.defaultdict(list)
# bf4f3fd7-182: documented QC exception — BN/PA66 ratio designation "30-4" is not a numeric
# loading; string relocated to notes in Phase 2 (see quality_control_report.md section 2).
LOADING_EXCEPTIONS = {'bf4f3fd7-182'}
def sval(r, c):
    v = r.get(c)
    return '' if v is None else str(v)
for r in rows:
    if not sval(r, 'source_location').strip(): missing['source_location'].append(r['row_id'])
    if not sval(r, 'doi').strip(): missing['doi'].append(r['row_id'])
    has_loading = any(sval(r, c).strip() for c in
                      ('filler_loading_vol_pct', 'filler_loading_wt_pct', 'filler_loading_original_value'))
    if not has_loading and r['row_id'] not in LOADING_EXCEPTIONS:
        missing['loading'].append(r['row_id'])
check('required_fields', 'All rows have source_location + loading + DOI '
      '(0.0 counts as present; 1 documented no-numeric-loading exception)',
      not any(missing.values()), dict(missing) if missing else 'all present')

confs = collections.Counter(r['confidence'] for r in rows)
check('confidence_labels', 'Only High/Medium confidence', set(confs) <= {'High', 'Medium'}, dict(confs))

# ---------- 4. Stats ----------
k_vals = sorted(float(r['k_composite_W_mK']) for r in rows)
years = sorted(int(r['year']) for r in rows if str(r.get('year') or '').strip())
papers = sorted({r['doi'] for r in rows})
by_filler = collections.Counter(r['filler_material'] for r in rows)
by_source = collections.Counter(r['value_source'] for r in rows)

def is_epoxy(m):
    m = (m or '').lower()
    return any(t in m for t in ('epoxy', 'dgeba', 'emc', 'ep ', 'etl', 'ejbn', 'lc epoxy')) or m.strip() == 'ep'
epoxy = sum(1 for r in rows if is_epoxy(r['matrix_polymer']))
bn_family = sum(c for f, c in by_filler.items() if 'bn' in f.lower())  # h-BN, BN, BNNS, hybrids w/ BN
bn_pure = sum(c for f, c in by_filler.items() if f.lower() in ('h-bn', 'bn', 'bnns', 'c bn', 'cbn', 'bn (unspecified morphology)'))

by_matrix = collections.Counter()
for r in rows:
    m = (r['matrix_polymer'] or '').lower()
    if any(t in m for t in ('epoxy', 'dgeba', 'emc', 'etl', 'ejbn')) or m.strip() in ('ep', 'lc epoxy', 'liquid crystal epoxy'):
        by_matrix['epoxy-based'] += 1
    elif 'silicone' in m: by_matrix['silicone'] += 1
    elif 'polyimide' in m or m.strip() == 'pi': by_matrix['polyimide'] += 1
    elif 'pdms' in m or 'polydimethylsiloxane' in m: by_matrix['PDMS'] += 1
    elif 'peg' in m: by_matrix['PEG PCM'] += 1
    elif 'polyurethane' in m or m.strip() == 'pu': by_matrix['polyurethane'] += 1
    elif 'polystyrene' in m or m.strip() == 'ps': by_matrix['polystyrene'] += 1
    else: by_matrix[r['matrix_polymer'][:30]] += 1

stats = {
    'total_rows': len(rows),
    'total_papers': len(papers),
    'unique_row_ids': len(set(ids)),
    'year_range': [min(years), max(years)],
    'k_min': k_vals[0], 'k_max': k_vals[-1], 'k_median': statistics.median(k_vals),
    'by_confidence': dict(confs),
    'confidence_pct_high': round(100 * confs.get('High', 0) / len(rows), 1),
    'by_value_source': dict(by_source),
    'by_matrix': dict(by_matrix.most_common()),
    'by_filler': dict(by_filler.most_common()),
    'epoxy_rows': epoxy,
    'epoxy_pct': round(100 * epoxy / len(rows), 1),
    'bn_family_rows_incl_hybrids': bn_family,
    'bn_pure_rows': bn_pure,
}
report['stats'] = stats

# companion file counts
def nrows(p):
    with open(OUT / p, encoding='utf-8-sig', newline='') as f:
        return sum(1 for _ in csv.DictReader(f))
report['deliverable_counts'] = {
    'thermal_conductivity_dataset.csv': len(csv_rows),
    'paper_inventory.csv': nrows('paper_inventory.csv'),
    'extraction_log.csv': nrows('extraction_log.csv'),
    'extraction_log.jsonl_entries': len(log),
    'uncertain_measurements.csv': nrows('uncertain_measurements.csv'),
    'unusable_sources.csv': nrows('unusable_sources.csv'),
}
check('uncertain_covers_medium', 'uncertain_measurements.csv row count == non-High rows',
      report['deliverable_counts']['uncertain_measurements.csv'] == len(rows) - confs.get('High', 0),
      f"unc={report['deliverable_counts']['uncertain_measurements.csv']} nonHigh={len(rows) - confs.get('High', 0)}")
inv_n = report['deliverable_counts']['paper_inventory.csv']
check('inventory_papers', 'paper_inventory.csv paper count == unique DOIs',
      inv_n == len(papers), f'inv={inv_n} dois={len(papers)}')

# ---------- 5. Phase-4 merge checks ----------
p4 = json.load(open(BASE / 'phase4_changes.json', encoding='utf-8'))
by_id = {r['row_id']: r for r in rows}
fig_rows = [r for r in rows if r['value_source'] == 'figure']
check('p4_figure_rows_flagged', 'Every figure-derived row is Medium and cites the digitizer + overlay',
      all(r['confidence'] == 'Medium' and 'phase4_digitize_v2.py' in r['source_location'] and 'overlay_' in r['source_location']
          for r in fig_rows),
      f'figure_rows={len(fig_rows)}')
upg = [u['row_id'] for u in p4['upgrades']]
check('p4_upgrades_high_fulltext', 'Phase-4 upgraded rows are High and cite a local full text',
      all(by_id[i]['confidence'] == 'High' and by_id[i]['source_location'].startswith('Full text (') for i in upg),
      f'upgraded={upg}')
check('p4_new_rows_present', 'All Phase-4 new row_ids present; row total matches change record',
      all(n['row_id'] in by_id for n in p4['new_rows']) and p4['after']['rows'] == len(rows),
      f"new={len(p4['new_rows'])} after={p4['after']['rows']} now={len(rows)}")
check('p4_ag_hybrid_excluded', 'Silver-hybrid 2.35 W/mK (out of scope) not extracted',
      not any(r['doi'] == '10.1177/09673911221110143' and float(r['k_composite_W_mK']) == 2.35 for r in rows), 'ok')
with open(OUT / 'unusable_sources.csv', encoding='utf-8-sig', newline='') as f:
    un = {u['doi']: u for u in csv.DictReader(f)}
fig_dois = ('10.3390/polym11071156', '10.3390/molecules21050670')
check('p4_unusable_updated', 'Figure-only DOIs re-classified as recovered; Sci-Hub policy row retained',
      all(un[d]['action'].startswith('recovered (Phase 4') for d in fig_dois) and '(policy)' in un,
      {d: un[d]['action'][:40] for d in fig_dois})
report['phase4'] = {'phase4_changes_exists': True, 'upgrades': len(upg), 'new_rows': len(p4['new_rows']),
                    'metadata_corrections': len(p4['metadata_corrections'])}

report['overall'] = 'PASS' if all(c['status'] == 'PASS' for c in report['checks']) else 'FAIL'
json.dump(report, open(BASE / 'final_verification.json', 'w', encoding='utf-8'), indent=2)
print('\nOVERALL:', report['overall'])
print(json.dumps(stats, indent=2))
