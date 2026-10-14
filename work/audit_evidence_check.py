# NEW FILE (audit-only). Automated evidence checks for every dataset row.
# Writes work/audit_phase1_rows.json. Does not modify production data.
import csv, json, os, re, collections, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

rows = list(csv.DictReader(open(os.path.join(ROOT, 'thermal_conductivity_dataset.csv'), encoding='utf-8-sig')))

def load_ft(doi):
    p = os.path.join(BASE, 'fulltext', doi.replace('/', '_') + '.txt')
    if not os.path.exists(p):
        return None
    return open(p, encoding='utf-8', errors='replace').read()

def variants(x):
    """Possible printed forms of a number."""
    out = set()
    try:
        v = float(x)
    except Exception:
        return {str(x)} if x else set()
    out.add(str(x))
    out.add(f'{v:g}')
    out.add(f'{v:.2f}'.rstrip('0').rstrip('.'))
    out.add(f'{v:.3f}'.rstrip('0').rstrip('.'))
    out.add(f'{v:.4f}'.rstrip('0').rstrip('.'))
    out.add(f'{v:.1f}')
    return {s for s in out if s and s not in ('', '.')}

def find_any(text, strs):
    hits = []
    for s in strs:
        if s and s in text:
            hits.append(s)
    return hits

# --- duplicate detection (doi+filler+loading+k) ---
dupkey = collections.defaultdict(list)
for i, r in enumerate(rows):
    k = (r['doi'], r['filler_material'], r['filler_loading_wt_pct'], r['filler_loading_vol_pct'], r['k_composite_W_mK'])
    dupkey[k].append(i)
dup_partner = {}
for k, idxs in dupkey.items():
    if len(idxs) > 1:
        for j in idxs[1:]:
            dup_partner[rows[j]['row_id']] = rows[idxs[0]]['row_id']

ft_cache = {}
results = []
for r in rows:
    doi = r['doi']
    if doi not in ft_cache:
        ft_cache[doi] = load_ft(doi)
    ft = ft_cache[doi]
    rid = r['row_id']
    findings = []
    status = None

    if ft is None:
        status = 'unverifiable'
        findings.append('no fulltext file on disk')
        k_hits, loc_hits, load_hits = [], [], []
    else:
        k_hits = find_any(ft, variants(r['k_original_value']))
        # key numbers from source_location
        loc_nums = re.findall(r'\d+\.?\d*', r['source_location'])
        loc_hits = find_any(ft, set(loc_nums))
        # distinctive words from source_location (alphabetic tokens > 3 chars)
        words = [w for w in re.findall(r'[A-Za-z]{4,}', r['source_location']) if w.lower() not in
                 {'table','text','figure','results','abstract','wt','value','values','paper','discussion'}]
        word_hits = sum(1 for w in words if w.lower() in ft.lower())
        load_cands = set()
        for fld in ('filler_loading_wt_pct', 'filler_loading_vol_pct'):
            if r[fld].strip():
                load_cands |= variants(r[fld])
        load_hits = find_any(ft, load_cands)

        if not k_hits:
            findings.append('k value string not found in fulltext')
        if loc_nums and len(loc_hits) < len(set(loc_nums)) * 0.5:
            findings.append(f'source_location numbers only partially found ({len(set(loc_hits))}/{len(set(loc_nums))})')
        if words and word_hits < max(1, len(words) // 3):
            findings.append('source_location wording largely absent from fulltext')
        if load_cands and not load_hits:
            findings.append('loading value not found in fulltext')

    # non-numeric values in numeric columns
    for c in ('filler_loading_vol_pct', 'filler_loading_wt_pct', 'filler_loading_original_value',
              'k_matrix_W_mK', 'filler_mean_size_um', 'measurement_temperature_C', 'k_original_value'):
        v = str(r[c]).strip()
        if v:
            try:
                float(v)
            except Exception:
                findings.append(f'non-numeric value in numeric column {c}: {v!r}')

    # physical plausibility flags (flag only)
    try:
        k = float(r['k_composite_W_mK'])
        if k < 0.1 or k > 100:
            findings.append(f'k outside 0.1-100 screening band: {k}')
    except Exception:
        findings.append('non-numeric k_composite')
    for c in ('filler_loading_wt_pct', 'filler_loading_vol_pct'):
        try:
            v = float(r[c])
            if v > 100 or v < 0:
                findings.append(f'loading out of range in {c}: {v}')
        except Exception:
            pass

    if rid in dup_partner:
        status = 'duplicate_measurement'
        findings.append(f'duplicate of row {dup_partner[rid]} (same doi/filler/loading/k)')
    elif ft is None:
        status = 'unverifiable'
    elif not k_hits:
        status = 'unsupported_source_location'
    elif findings:
        status = 'verified_with_warning'
    else:
        status = 'verified'  # automated evidence match (full k + numbers + wording found)

    results.append({
        'row_id': rid, 'doi': doi, 'verification_status': status,
        'evidence_inspected': 'fulltext:' + (doi.replace('/', '_') + '.txt' if ft is not None else 'MISSING'),
        'k_original_value': r['k_original_value'], 'k_original_unit': r['k_original_unit'],
        'k_composite_W_mK': r['k_composite_W_mK'],
        'filler_loading': r['filler_loading_original_value'] or r['filler_loading_wt_pct'] or r['filler_loading_vol_pct'],
        'source_location': r['source_location'][:200],
        'k_found_in_text': bool(k_hits) if ft is not None else None,
        'findings': findings,
    })

summary = collections.Counter(x['verification_status'] for x in results)
print('STATUS COUNTS:', dict(summary))
flagged = [x for x in results if x['findings']]
print('rows with findings:', len(flagged))
for x in flagged:
    print(' ', x['row_id'], x['doi'], x['verification_status'], '|', '; '.join(x['findings'])[:180])

out = {'summary': dict(summary), 'rows': results}
json.dump(out, open(os.path.join(BASE, 'audit_phase1_rows.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote work/audit_phase1_rows.json')
