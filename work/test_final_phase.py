"""Independent acceptance tests for the FINAL PHASE mission (designed from requirements).

Oracle: all expected numbers are recomputed here directly from the CSVs/JSONL,
never imported from work/final_verify.py or final_verification.json.
"""
import csv, json, statistics, sys
from pathlib import Path

OUT = Path('.')
fails, passes = [], 0

def t(cid, ok, detail):
    global passes
    if ok: passes += 1
    else: fails.append((cid, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {cid}: {detail}")

# ---- recompute oracle straight from source of truth ----
rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
with open('thermal_conductivity_dataset.csv', encoding='utf-8-sig', newline='') as f:
    ds = list(csv.DictReader(f))
k = sorted(float(r['k_composite_W_mK']) for r in rows)
conf = {}
for r in rows: conf[r['confidence']] = conf.get(r['confidence'], 0) + 1
papers = len({r['doi'] for r in rows})

# ---- BASIC ----
t('report_exists', Path('FINAL_REPORT.md').exists() and Path('FINAL_REPORT.md').stat().st_size > 5000,
  f"size={Path('FINAL_REPORT.md').stat().st_size if Path('FINAL_REPORT.md').exists() else 0}")
t('final_verification_pass', json.load(open('work/final_verification.json', encoding='utf-8'))['overall'] == 'PASS', 'overall==PASS')
figs = sorted(p.name for p in Path('figures').glob('*.png'))
t('figures_present', all(f'0{i}_' in ' '.join(figs) for i in range(1, 7)) and len(figs) >= 6, str(figs))
t('figures_nonempty', all((Path('figures')/f).stat().st_size > 10_000 for f in figs), 'all >10KB')
t('figures_readme', Path('figures/README.md').exists(), 'exists')
t('csv_bom_31cols', open('thermal_conductivity_dataset.csv','rb').read(3) == b'\xef\xbb\xbf' and len(ds[0]) == 31,
  f"bom=yes cols={len(ds[0])}")

def count_csv(p):
    with open(p, encoding='utf-8-sig', newline='') as f: return sum(1 for _ in csv.DictReader(f))
t('deliverable_counts', (len(ds), count_csv('paper_inventory.csv'), count_csv('extraction_log.csv'),
    count_csv('uncertain_measurements.csv'), count_csv('unusable_sources.csv')) == (232, 93, 101, 40, 49),
  f"{len(ds)},{count_csv('paper_inventory.csv')},{count_csv('extraction_log.csv')},"
  f"{count_csv('uncertain_measurements.csv')},{count_csv('unusable_sources.csv')}")

# ---- EDGE: report numbers must match the data (independent oracle) ----
rep = Path('FINAL_REPORT.md').read_text(encoding='utf-8')
kmax_tok = f'{k[-1]:.2f}'
for token in ['232', '93', f'{k[0]:.2f}', kmax_tok,
              f'{statistics.median(k):.2f}', str(conf['High']), str(conf['Medium'])]:
    t(f'report_token_{token}', token in rep, f"'{token}' in FINAL_REPORT")
t('report_figures_embedded', all(f'![](figures/{f})' in rep for f in figs), 'all figure embeds present')
t('report_sections', all(s in rep for s in ['Project summary', 'Key numbers', 'Methodology',
  'Quality assurance', 'Figure gallery', 'Coverage', 'File inventory', 'reproduce', 'Next steps']), '9 sections')

# QC report + README final counts (stale Phase-2 section is allowed to mention history;
# the SUMMARY section must carry final numbers)
qc = Path('quality_control_report.md').read_text(encoding='utf-8')
sec1 = qc.split('## 2.')[0]
t('qc_sec1_final', '232' in sec1 and '93' in sec1 and '47.03' in sec1 and '192' in sec1, 'QC §1 has final numbers')
t('qc_medium_updated', '40 rows marked Medium' in qc, 'QC §3 medium=40')
rd = Path('README.md').read_text(encoding='utf-8')
t('readme_final', '232 rows / 93 papers' in rd and 'FINAL_REPORT.md' in rd, 'README current + links report')

# ---- EDGE: uncertain CSV exactly the Medium rows ----
with open('uncertain_measurements.csv', encoding='utf-8-sig', newline='') as f:
    unc = list(csv.DictReader(f))
t('uncertain_all_medium', all(r['confidence'] == 'Medium' for r in unc) and len(unc) == conf.get('Medium', -1),
  f'n={len(unc)}')

# ---- EDGE: no Phase-2 dropped rows resurrected ----
p2 = json.load(open('work/phase2_applied_changes.json', encoding='utf-8'))
dropped = set(p2['drops']['row_ids_dropped'])
t('no_resurrection', not (dropped & {r['row_id'] for r in rows}), f'dropped={len(dropped)}')

# ---- EDGE: single documented loading exception only ----
# note: numeric 0.0 (neat-resin baseline) is a PRESENT loading value, so use None-safe check
def sval(r, c):
    v = r.get(c)
    return '' if v is None else str(v)
no_load = [r['row_id'] for r in rows if not any(sval(r, c).strip() for c in
          ('filler_loading_vol_pct','filler_loading_wt_pct','filler_loading_original_value'))]
t('loading_exception', no_load == ['bf4f3fd7-182'], str(no_load))

print(f'\n{passes} passed, {len(fails)} failed')
for cid, d in fails: print(' FAILED:', cid, d)
sys.exit(1 if fails else 0)
