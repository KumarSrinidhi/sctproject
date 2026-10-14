import json, csv, os, collections
from pathlib import Path

BASE = Path(r'work')
OUT = Path('.')

rows = [json.loads(l) for l in open(BASE/'rows_raw.jsonl', encoding='utf-8')]
log = [json.loads(l) for l in open(BASE/'extraction_log.jsonl', encoding='utf-8')]
cands = json.load(open(BASE/'candidates.json', encoding='utf-8')) if (BASE/'candidates.json').exists() else []
wave2 = json.load(open(BASE/'wave2_fetch.json', encoding='utf-8')) if (BASE/'wave2_fetch.json').exists() else []
epmc2 = json.load(open(BASE/'epmc_wave2.json', encoding='utf-8')) if (BASE/'epmc_wave2.json').exists() else []

# ========== 1. thermal_conductivity_dataset.csv ==========
COLS = ['row_id', 'doi', 'source_url', 'paper_title', 'year', 'matrix_polymer', 'curing_agent',
        'filler_material', 'filler_material_original', 'filler_shape', 'filler_aspect_ratio',
        'filler_mean_size_um', 'size_distribution', 'filler_loading_vol_pct', 'filler_loading_wt_pct',
        'filler_loading_original_value', 'filler_loading_original_unit', 'functionalization',
        'filler_alignment', 'processing_method', 'k_matrix_W_mK', 'k_composite_W_mK', 'k_direction',
        'measurement_method', 'measurement_temperature_C', 'k_original_value', 'k_original_unit',
        'value_source', 'source_location', 'confidence', 'notes']

with open(OUT/'thermal_conductivity_dataset.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f'thermal_conductivity_dataset.csv: {len(rows)} rows')

# ========== 2. paper_inventory.csv ==========
papers = {}
for r in rows:
    d = r['doi']
    if d not in papers:
        papers[d] = {'doi': d, 'paper_title': r['paper_title'], 'year': r['year'],
                     'source_url': r['source_url'], 'rows_extracted': 0,
                     'filler_materials': set(), 'matrix_polymers': set(),
                     'k_min': 999, 'k_max': 0}
    p = papers[d]
    p['rows_extracted'] += 1
    p['filler_materials'].add(r['filler_material'])
    p['matrix_polymers'].add(r['matrix_polymer'])
    k = float(r['k_composite_W_mK'])
    p['k_min'] = min(p['k_min'], k); p['k_max'] = max(p['k_max'], k)

inv_cols = ['doi','paper_title','year','source_url','rows_extracted','filler_materials','matrix_polymers','k_min_W_mK','k_max_W_mK']
with open(OUT/'paper_inventory.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=inv_cols)
    w.writeheader()
    for d in sorted(papers, key=lambda x: papers[x]['doi']):
        p = papers[d]
        w.writerow({
            'doi': p['doi'], 'paper_title': p['paper_title'], 'year': p['year'],
            'source_url': p['source_url'], 'rows_extracted': p['rows_extracted'],
            'filler_materials': '; '.join(sorted(p['filler_materials'])),
            'matrix_polymers': '; '.join(sorted(p['matrix_polymers'])),
            'k_min_W_mK': p['k_min'], 'k_max_W_mK': p['k_max'],
        })
print(f'paper_inventory.csv: {len(papers)} papers')

# ========== 3. extraction_log.csv ==========
log_cols = ['candidate_id','doi','paper_title','date_processed','access_result','files_inspected',
            'tables_inspected','figures_inspected','candidate_measurements','rows_appended',
            'unit_conversions','duplicate_checks','qc_findings','rows_rejected_at_append']
with open(OUT/'extraction_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=log_cols, extrasaction='ignore')
    w.writeheader()
    for e in log:
        row = {c: e.get(c, '') for c in log_cols}
        rej = e.get('rows_rejected_at_append', [])
        if rej:
            row['rows_rejected_at_append'] = '; '.join(f'{rid}:{reason}' for rid, reason in rej)
        w.writerow(row)
print(f'extraction_log.csv: {len(log)} entries')

# ========== 4. uncertain_measurements.csv (Medium confidence) ==========
uncertain = [r for r in rows if r['confidence'] != 'High']
with open(OUT/'uncertain_measurements.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for r in uncertain:
        w.writerow(r)
print(f'uncertain_measurements.csv: {len(uncertain)} rows (Medium/Low confidence)')

# ========== 5. unusable_sources.csv ==========
unusable = [
    {'doi': '10.1088/1361-6528/ac0470', 'reason': 'IOP Radware captcha (txt replacement, not PDF)', 'action': 'unusable'},
    {'doi': '10.1088/1742-6596/1003/1/012082', 'reason': 'IOP Radware captcha', 'action': 'unusable'},
    {'doi': '10.1088/1757-899x/274/1/012043', 'reason': 'IOP Radware captcha', 'action': 'unusable'},
    {'doi': '10.1515/polyeng-2025-0193', 'reason': 'Wiley blocked (403), no EPMC route', 'action': 'unusable'},
    {'doi': '10.1002/pc.71726', 'reason': 'Wiley blocked (403), no EPMC route', 'action': 'unusable'},
    {'doi': '10.1002/pc.71558', 'reason': 'Wiley blocked (403), no EPMC route', 'action': 'unusable'},
    {'doi': '10.1002/smll.75841', 'reason': 'Wiley blocked (403), no EPMC route', 'action': 'unusable'},
    {'doi': '10.1002/slct.202507155', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/app.56949', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/pat.70120', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/inf2.70139', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/pc.70149', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/pc.28534', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1002/pc.70279', 'reason': 'Wiley blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.compositesa.2026.110044', 'reason': 'Elsevier blocked (403), no EPMC route', 'action': 'unusable'},
    {'doi': '10.1016/j.compositesb.2025.112764', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.cej.2026.180373', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.carbon.2026.121402', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.porgcoat.2025.109667', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.ceramint.2026.04.021', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.apsusc.2025.163268', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.eurpolymj.2024.113084', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.matlet.2025.139278', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1016/j.compstruct.2025.119723', 'reason': 'Elsevier blocked (403)', 'action': 'unusable'},
    {'doi': '10.1088/1361-6463/ae6b9b', 'reason': 'IOP blocked (403/captcha)', 'action': 'unusable'},
    {'doi': '10.1049/hve2.70112', 'reason': 'IET blocked', 'action': 'unusable'},
    {'doi': '10.1007/s10853-026-12616-z', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s10854-026-18087-x', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s11837-025-07613-7', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s13726-025-01550-7', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s10965-024-04142-w', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s10570-024-05737-8', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s10443-023-10195-9', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1007/s00289-025-06054-1', 'reason': 'Springer blocked (403)', 'action': 'unusable'},
    {'doi': '10.1063/5.0205196', 'reason': 'AIP blocked', 'action': 'unusable'},
    {'doi': '10.1021/acsapm.4c01099', 'reason': 'ACS blocked', 'action': 'unusable'},
    {'doi': '10.1177/09540083251319488', 'reason': 'SAGE blocked', 'action': 'unusable'},
    {'doi': '10.31248/ajps2025.124', 'reason': 'Modeling paper (Debye relaxation model), no experimental k values', 'action': 'excluded_modeling'},
    {'doi': '10.3390/ma13163634', 'reason': 'Review article', 'action': 'excluded_review'},
    {'doi': '10.3390/ma12091522', 'reason': 'Carbon fillers (out of BN/AlN scope)', 'action': 'excluded_scope'},
    {'doi': '10.3390/polym11071156', 'reason': 'Figure-only k values (no text numeric)', 'action': 'excluded_figure_only'},
    {'doi': '10.3390/molecules21050670', 'reason': 'Own data figure-only; text values are literature comparisons', 'action': 'excluded_figure_only'},
    {'doi': '10.14314/polimery.2017.560', 'reason': 'Abstract only, no k values', 'action': 'excluded_no_data'},
    {'doi': '10.3390/nano9101396', 'reason': 'Relative % increase only, no absolute k in text', 'action': 'excluded_no_absolute_k'},
    {'doi': '10.3390/polym10030277', 'reason': 'No absolute k for own data in text', 'action': 'excluded_no_absolute_k'},
    {'doi': '10.1039/c8ra10645b', 'reason': 'No absolute k hits in text', 'action': 'excluded_no_absolute_k'},
    {'doi': '10.3390/molecules28093797', 'reason': 'PCM (paraffin/LA-ODE) matrix, out of epoxy/BN primary scope', 'action': 'excluded_scope'},
    {'doi': '10.3390/polym13132161', 'reason': 'Al2O3/AlN literature values only; own data not BN/AlN primary', 'action': 'excluded_scope'},
]
with open(OUT/'unusable_sources.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=['doi','reason','action'])
    w.writeheader()
    for u in unusable:
        w.writerow(u)
print(f'unusable_sources.csv: {len(unusable)} entries')

# ========== stats for QC report ==========
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
k_vals = [float(r['k_composite_W_mK']) for r in rows]

stats = {
    'total_rows': len(rows),
    'total_papers': len(papers),
    'by_matrix_top': by_matrix.most_common(10),
    'by_filler': by_filler.most_common(),
    'by_confidence': by_conf.most_common(),
    'by_value_source': by_source.most_common(),
    'k_min': min(k_vals), 'k_max': max(k_vals), 'k_median': sorted(k_vals)[len(k_vals)//2],
    'year_range': (min(int(r['year']) for r in rows if r['year']), max(int(r['year']) for r in rows if r['year'])),
}
json.dump(stats, open(BASE/'deliverable_stats.json','w',encoding='utf-8'), indent=2, default=str)
print('stats saved')
print(stats)
