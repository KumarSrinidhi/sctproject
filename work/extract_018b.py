import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E23 retry: 10.1039/c8ra10211b =====
E23 = dict(doi='10.1039/c8ra10211b', source_url='https://doi.org/10.1039/c8ra10211b',
           paper_title='3D BN/PA66 aerogel scaffolds for epoxy composites with enhanced thermal conductivity',
           year=2018)
rows = [dict(
    matrix_polymer='Epoxy (E-51) with PA66 aerogel scaffold', curing_agent='',
    filler_material='BN', filler_material_original='3D BN/PA66-30-4 (BN 30, PA66 4), epoxy impregnated',
    filler_shape='hybrid', functionalization='3D aerogel scaffold',
    filler_loading_wt_pct='', filler_loading_original_value='', filler_loading_original_unit='',
    k_composite_W_mK='0.6', k_original_value='0.6', k_original_unit='W m−1 K−1',
    measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.15',
    processing_method='3D BN/PA66 aerogel scaffold from freeze-drying, then epoxy impregnation',
    source_location='Results: 3D BN/PA66-30-4 composite -> 0.6 W m−1 K−1 (5x neat epoxy)',
    notes='3D aerogel scaffold architecture. Loading designation BN/PA66 ratio (30:4), not wt%.')]
n, p = append_rows(E23, rows, dict(candidate_id='P060', doi=E23['doi'], paper_title=E23['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_c8ra10211b.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='random BN/EP-4 0.2 already extracted in prior row of same paper',
    qc_findings='retry: loading designation non-numeric, extracted without loading field'))
print(f'RETRY E23: {n}')
