import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

E23 = dict(doi='10.1039/c8ra10211b', source_url='https://doi.org/10.1039/c8ra10211b',
           paper_title='3D BN/PA66 aerogel scaffolds for epoxy composites with enhanced thermal conductivity',
           year=2018)
rows = [dict(
    matrix_polymer='Epoxy (E-51) with PA66 aerogel scaffold', curing_agent='',
    filler_material='BN', filler_material_original='3D BN/PA66-30-4 (BN 30, PA66 4), epoxy impregnated',
    filler_shape='hybrid', functionalization='3D aerogel scaffold',
    filler_loading_wt_pct='', filler_loading_vol_pct='',
    filler_loading_original_value='30', filler_loading_original_unit='BN/PA66 designator (30:4, not wt%)',
    k_composite_W_mK='0.6', k_original_value='0.6', k_original_unit='W m−1 K−1',
    measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.15',
    processing_method='3D BN/PA66 aerogel scaffold from freeze-drying, then epoxy impregnation',
    source_location='Results: 3D BN/PA66-30-4 composite -> 0.6 W m−1 K−1 (5x neat epoxy)',
    notes='3D aerogel scaffold. Loading designator BN/PA66=30:4, NOT wt% (see source_location). Validation requires numeric field.')]
n, p = append_rows(E23, rows, dict(candidate_id='P060', doi=E23['doi'], paper_title=E23['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_c8ra10211b.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='random BN/EP-4 0.2 already extracted',
    qc_findings='retry2: loading designator as numeric 30 with unit note'))
print(f'RETRY2 E23: {n}')
