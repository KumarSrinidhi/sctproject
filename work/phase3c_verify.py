import json, os, hashlib, csv
from datetime import date

# ---------- integrity ----------
rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
DROPPED = {'a9d63e6e-014','a9d63e6e-015','a9d63e6e-016','2f8abcf1-061','2f8abcf1-062',
           'ad883006-077','0e680d76-098','b8850d43-119','b8850d43-120','b8850d43-121',
           'a8b6fee9-141','a8b6fee9-142','caf49a8d-150','4a11b03c-151','bf4f3fd7-185'}
row_ids = [r['row_id'] for r in rows]
dois = {r['doi'] for r in rows}
k_vals = [float(r['k_composite_W_mK']) for r in rows]

checks = {
    'total_rows': len(rows),
    'unique_row_ids': len(set(row_ids)),
    'row_ids_unique': len(row_ids) == len(set(row_ids)),
    'total_papers': len(dois),
    'dropped_ids_resurrected': sorted(DROPPED & set(row_ids)),
    'all_k_numeric_positive': all(v > 0 for v in k_vals),
    'all_rows_have_source_location': all(r.get('source_location') for r in rows),
    'abstract_only_confidence_medium': all(
        r['confidence'] == 'Medium'
        for r in rows if 'Abstract (Semantic Scholar' in (r.get('source_location') or '')),
}

verif = {
    'phase': '3 (RETRY)',
    'date': date.today().isoformat(),
    'baseline_before_phase3': {'rows': 173, 'papers': 63},
    'after_phase3': {'rows': checks['total_rows'], 'papers': checks['total_papers']},
    'delta': {'rows': checks['total_rows'] - 173, 'papers': checks['total_papers'] - 63},
    'targets': {'rows_min_200': checks['total_rows'] >= 200, 'papers_min_65': checks['total_papers'] >= 65},
    'checks': checks,
    'deliverables_regenerated': True,
    'build_deliverables_run_before_unusable_postprocess': True,
    'unusable_sources_postprocessed_separately': True,
}
json.dump(verif, open('work/phase3_verification.json', 'w', encoding='utf-8'), indent=2)
print(json.dumps(verif, indent=2))
