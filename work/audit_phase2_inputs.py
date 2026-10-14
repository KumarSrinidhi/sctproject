"""Phase 2 prep (READ-ONLY): corrected titles, loading fixes, drop lists, non-numeric cells.

Writes ONLY work/audit_phase2_inputs.json. Never modifies any deliverable.
Exit 0 = all checks passed (baseline hashes intact, 11 titles fetched, dup logic
reproduces the audited 9 intra-paper pairs). Exit 1 = any check failed.
"""
import csv, json, hashlib, urllib.request, urllib.parse, collections, sys

BASE_HASHES = {
    'thermal_conductivity_dataset.csv': '78999ab6f289b68d',
    'paper_inventory.csv': '6d6ceca2efe18ec9',
    'extraction_log.csv': 'bd459be54b86bd3e',
    'uncertain_measurements.csv': 'cc8ab3b308051a03',
    'unusable_sources.csv': 'c0c1ec7c18fd4e97',
    'quality_control_report.md': '6cb2e76643e7f981',
    'README.md': '05c04bc3f6e24214',
}
EXPECTED_INTRA_DROP_SUFFIXES = {'061', '062', '077', '098', '119', '120', '121', '150', '185'}
WRONG_TITLE_DOIS = [
    '10.1038/s41598-018-19945-3', '10.3390/polym11121990', '10.3390/polym11081335',
    '10.3390/polym13030456', '10.3390/nano15120936', '10.3390/polym18050648',
    '10.1039/c8ra10211b', '10.3390/ijms24098221', '10.3390/polym16081169',
    '10.3390/polym17111507', '10.3390/nano8120997',
]
DROP_CROSS_SUFFIXES = ['014', '015', '016', '141', '142']  # pending domain approval
DROP_OUT_OF_SCOPE = ['151']                                # pending approval (drop vs re-source)
LOADING_DOI = '10.3390/polym13060955'
# Table 1 "Compositions by weight": true BN wt% = BN / (epoxy + BN + curing agent)
GRADE_WT = {
    ('ETL', '60'): round(60 / (40 + 60 + 26.7 + 0.8) * 100, 1),
    ('ETL', '70'): round(70 / (30 + 70 + 20.0 + 0.6) * 100, 1),
    ('EJ', '60'): round(60 / (40 + 60 + 13.3) * 100, 1),
    ('EJ', '65'): round(65 / (35 + 65 + 11.7) * 100, 1),
}
NUMERIC_COLS = ['k_composite_W_mK', 'filler_loading_wt_pct', 'filler_loading_vol_pct',
                'filler_mean_size_um', 'measurement_temperature_C']


def sha16(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def crossref_title(doi):
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={'User-Agent': 'ARGUS-audit/1.0 (mailto:audit@example.org)'})
    with urllib.request.urlopen(req, timeout=25) as resp:
        msg = json.load(resp)['message']
    return (msg.get('title') or [''])[0]


def main():
    errors = []
    hash_state = {f: sha16(f) for f in BASE_HASHES}
    bad = [f for f, h in BASE_HASHES.items() if hash_state[f] != h]
    if bad:
        errors.append('baseline hash mismatch: %s' % bad)

    rows = list(csv.DictReader(open('thermal_conductivity_dataset.csv', encoding='utf-8-sig')))
    if len(rows) != 188:
        errors.append('expected 188 rows, got %d' % len(rows))

    # --- drop lists -------------------------------------------------------
    grp = collections.defaultdict(list)
    for r in rows:
        key = (r['doi'], r['filler_material'], r['filler_loading_wt_pct'],
               r['filler_loading_vol_pct'], r['k_composite_W_mK'])
        grp[key].append(r['row_id'])
    intra_drops = []
    for ids in grp.values():
        if len(ids) > 1:
            ordered = sorted(ids, key=lambda s: int(s.split('-')[-1]))
            intra_drops.extend(ordered[1:])
    suffix = {r['row_id'].split('-')[-1]: r['row_id'] for r in rows}
    if {i.split('-')[-1] for i in intra_drops} != EXPECTED_INTRA_DROP_SUFFIXES:
        errors.append('intra dup set differs from audited list: %s' % sorted(intra_drops))
    drop_cross = [suffix[s] for s in DROP_CROSS_SUFFIXES if s in suffix]
    drop_oos = [suffix[s] for s in DROP_OUT_OF_SCOPE if s in suffix]
    if len(drop_cross) != 5 or len(drop_oos) != 1:
        errors.append('cross/oos suffix resolution failed')

    # --- corrected titles (Crossref) --------------------------------------
    title_fixes = {}
    for doi in WRONG_TITLE_DOIS:
        cur = next((r['paper_title'] for r in rows if r['doi'] == doi), None)
        if cur is None:
            errors.append('doi missing from dataset: %s' % doi)
            continue
        try:
            title_fixes[doi] = {'current': cur, 'corrected': crossref_title(doi)}
        except Exception as exc:
            title_fixes[doi] = {'current': cur, 'corrected': None, 'error': str(exc)}
            errors.append('crossref fetch failed for %s: %s' % (doi, exc))

    # --- loading fixes (polym13060955) ------------------------------------
    loading_fixes = []
    for r in rows:
        if r['doi'] != LOADING_DOI:
            continue
        family = 'ETL' if r['matrix_polymer'].startswith('Epoxy-thiol') else 'EJ'
        grade = str(int(float(r['filler_loading_wt_pct'])))
        corrected = GRADE_WT[(family, grade)]
        loading_fixes.append({
            'row_id': r['row_id'], 'family': family, 'grade': grade,
            'matrix': r['matrix_polymer'], 'curing_agent': r['curing_agent'],
            'stored_wt_pct': r['filler_loading_wt_pct'],
            'corrected_wt_pct': corrected,
            'vol_pct': r['filler_loading_vol_pct'],
            'basis': '%s grade: BN/(epoxy+BN+curing agent) from Table 1 (compositions by weight)'
                     % family,
        })
    if len(loading_fixes) != 20:
        errors.append('expected 20 loading fixes, got %d' % len(loading_fixes))

    # --- non-numeric values (two distinct classes, audit D9) --------------
    numeric_col_violations = []   # text in genuinely numeric columns (schema violation)
    for r in rows:
        for col in NUMERIC_COLS:
            v = (r.get(col) or '').strip()
            if not v:
                continue
            try:
                float(v)
            except ValueError:
                numeric_col_violations.append({'row_id': r['row_id'], 'column': col, 'value': v})
    unparsable_original_strings = []  # composite strings the pipeline claimed to reject at append
    for r in rows:
        v = (r.get('filler_loading_original_value') or '').strip()
        if v:
            try:
                float(v)
            except ValueError:
                unparsable_original_strings.append(
                    {'row_id': r['row_id'], 'value': v,
                     'numeric_wt': r['filler_loading_wt_pct'], 'numeric_vol': r['filler_loading_vol_pct']})
    if len(numeric_col_violations) != 2:
        errors.append('expected 2 numeric-col violations, got %d' % len(numeric_col_violations))
    if len(unparsable_original_strings) != 7:
        errors.append('expected 7 unparsable original strings, got %d' % len(unparsable_original_strings))

    out = {
        'baseline_hashes': hash_state,
        'baseline_hashes_ok': not bad,
        'title_fixes': title_fixes,
        'loading_fixes': sorted(loading_fixes, key=lambda d: int(d['row_id'].split('-')[-1])),
        'drop_intra_recommended': sorted(intra_drops, key=lambda s: int(s.split('-')[-1])),
        'drop_cross_recommended': drop_cross,
        'drop_out_of_scope_recommended': drop_oos,
        'row_totals': {
            'current': len(rows),
            'after_intra': len(rows) - len(intra_drops),
            'after_intra_and_cross': len(rows) - len(intra_drops) - len(drop_cross),
            'after_all_recommended': len(rows) - len(intra_drops) - len(drop_cross) - len(drop_oos),
        },
        'numeric_col_violations': numeric_col_violations,
        'unparsable_original_strings': unparsable_original_strings,
        'pending_decisions': [
            'drop_cross list needs domain-owner approval (keep-side: d831a829-135..139 pressure series)',
            'row 4a11b03c-151: drop (recommended) vs re-source to original DOI',
            'sample-label fixes for rows 036 / 147 / 180 + hybrid convention (095, 151-153, 188) = judgment edits, applied at Phase 2',
        ],
        'errors': errors,
    }
    with open('work/audit_phase2_inputs.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print('hashes_ok=%s titles=%d/%d loading_fixes=%d intra_drops=%d cross_drops=%d oos=%d '
          'numviol=%d unparsable=%d'
          % (not bad, sum(1 for v in title_fixes.values() if v.get('corrected')),
             len(WRONG_TITLE_DOIS), len(loading_fixes), len(intra_drops),
             len(drop_cross), len(drop_oos),
             len(numeric_col_violations), len(unparsable_original_strings)))
    print('row_totals:', out['row_totals'])
    if errors:
        print('ERRORS:')
        for e in errors:
            print(' -', e)
        return 1
    print('OK -> work/audit_phase2_inputs.json (deliverables untouched)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
