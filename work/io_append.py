import json, os, sys, re, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(BASE, 'rows_raw.jsonl')
LOG = os.path.join(BASE, 'extraction_log.jsonl')

COLS = ['row_id', 'doi', 'source_url', 'paper_title', 'year', 'matrix_polymer', 'curing_agent',
        'filler_material', 'filler_material_original', 'filler_shape', 'filler_aspect_ratio',
        'filler_mean_size_um', 'size_distribution', 'filler_loading_vol_pct', 'filler_loading_wt_pct',
        'filler_loading_original_value', 'filler_loading_original_unit', 'functionalization',
        'filler_alignment', 'processing_method', 'k_matrix_W_mK', 'k_composite_W_mK', 'k_direction',
        'measurement_method', 'measurement_temperature_C', 'k_original_value', 'k_original_unit',
        'value_source', 'source_location', 'confidence', 'notes']

ALLOWED_K_UNIT = {  # to W/mK
    'w/mk': 1.0, 'w/m·k': 1.0, 'w m−1 k−1': 1.0, 'w m-1 k-1': 1.0, 'wm−1k−1': 1.0,
    'w/(m·k)': 1.0, 'w/m k': 1.0, 'w/m*k': 1.0, 'w⋅m−1⋅k−1': 1.0, 'w⋅m-1⋅k-1': 1.0,
    'w m−1k−1': 1.0, 'w/(m k)': 1.0,
    'mw/mk': 0.001, 'mw/m·k': 0.001, 'mw m−1 k−1': 0.001,
    'w/cmk': 100.0, 'w/cm·k': 100.0, 'w cm−1 k−1': 100.0,
    'w/mmk': 1000.0,
}

def normalize_k(value, unit):
    u = unit.strip().lower().replace('·', '·')
    u = re.sub(r'\s+', ' ', u)
    u2 = u.replace('·', '').replace('⋅', '')
    for k, f in ALLOWED_K_UNIT.items():
        if u == k or u2 == k.replace('·', '').replace('⋅', ''):
            return round(value * f, 6)
    # common unicode variants
    if 'w' in u and 'k' in u and ('m' in u):
        if 'mw' in u or 'milliw' in u:
            return round(value * 0.001, 6)
        if 'cm' in u:
            return round(value * 100.0, 6)
        if 'mm' in u and 'm−1' not in u and 'm-1' not in u:
            return round(value * 1000.0, 6)
        return round(value, 6)
    return None

def make_row_id(doi, seq):
    h = hashlib.md5((doi or 'nodoi').encode()).hexdigest()[:8]
    return f'{h}-{seq:03d}'

def append_rows(paper_meta, rows, log_entry):
    """paper_meta: dict with doi,title,year,source_url; rows: list of dicts (partial cols)."""
    existing = 0
    if os.path.exists(ROWS):
        existing = sum(1 for _ in open(ROWS, encoding='utf-8'))
    out = []
    problems = []
    for i, r in enumerate(rows, 1):
        full = {c: '' for c in COLS}
        # paper-level defaults from paper_meta (row-level values still win via update below)
        for k in ('doi', 'source_url', 'paper_title', 'year'):
            if paper_meta.get(k) not in (None, ''):
                full[k] = paper_meta[k]
        full.update(r)
        if not full['row_id']:
            full['row_id'] = make_row_id(paper_meta.get('doi'), existing + i)
        # validation
        k = full['k_composite_W_mK']
        if k == '' or k is None:
            problems.append((full['row_id'], 'missing k_composite'))
            continue
        try:
            k = float(k)
        except Exception:
            problems.append((full['row_id'], 'non-numeric k'))
            continue
        if k <= 0:
            problems.append((full['row_id'], 'non-positive k'))
            continue
        full['k_composite_W_mK'] = k
        if full['k_original_value'] not in ('', None):
            try:
                full['k_original_value'] = float(full['k_original_value'])
            except Exception:
                pass
        load_ok = (full['filler_loading_vol_pct'] not in ('', None) or
                   full['filler_loading_wt_pct'] not in ('', None) or
                   full['filler_loading_original_value'] not in ('', None))
        if not load_ok:
            problems.append((full['row_id'], 'missing loading'))
            continue
        if not full['source_location']:
            problems.append((full['row_id'], 'missing source_location'))
            continue
        for fld in ('filler_loading_vol_pct', 'filler_loading_wt_pct', 'k_matrix_W_mK',
                    'filler_aspect_ratio', 'filler_mean_size_um', 'measurement_temperature_C',
                    'filler_loading_original_value'):
            if full[fld] not in ('', None):
                try:
                    full[fld] = float(full[fld])
                except Exception:
                    problems.append((full['row_id'], f'non-numeric {fld}'))
        out.append(full)
    with open(ROWS, 'a', encoding='utf-8') as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    entry = dict(log_entry)
    entry['rows_appended'] = len(out)
    entry['rows_rejected_at_append'] = problems
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"appended {len(out)} rows; rejected {len(problems)}")
    for p in problems:
        print('  REJECT:', p)
    return len(out), problems

if __name__ == '__main__':
    print('io_append ready; cols:', len(COLS))
