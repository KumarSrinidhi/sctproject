import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E23: 10.1039/c8ra10211b (3D BN/PA66/epoxy hybrid) =====
E23 = dict(doi='10.1039/c8ra10211b', source_url='https://doi.org/10.1039/c8ra10211b',
           paper_title='3D BN/PA66 aerogel scaffolds for epoxy composites with enhanced thermal conductivity',
           year=2018)
rows_E23 = [
    dict(matrix_polymer='Epoxy (E-51) with PA66 aerogel scaffold', curing_agent='',
         filler_material='BN', filler_material_original='3D BN/PA66-30-4 (BN 30, PA66 4), epoxy impregnated',
         filler_shape='hybrid', functionalization='3D aerogel scaffold',
         filler_loading_wt_pct='', filler_loading_original_value='30-4', filler_loading_original_unit='BN/PA66 ratio designation (not wt%)',
         k_composite_W_mK='0.6', k_original_value='0.6', k_original_unit='W m−1 K−1',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.15',
         processing_method='3D BN/PA66 aerogel scaffold from freeze-drying, then epoxy impregnation',
         source_location='Results: 3D BN/PA66-30-4 composite -> 0.6 W m−1 K−1 (5x neat epoxy)',
         notes='3D aerogel scaffold architecture. Loading designation BN/PA66 ratio, not wt%.'),
    dict(matrix_polymer='Epoxy (E-51)', curing_agent='',
         filler_material='BN', filler_material_original='Random BN/EP-4 (random BN microplatelets)',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='', filler_loading_original_value='4', filler_loading_original_unit='BN loading designation EP-4 (figure)',
         k_composite_W_mK='0.2', k_original_value='0.2', k_original_unit='W m−1 K−1',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.15',
         processing_method='Random BN microplatelets in epoxy',
         source_location='Results: random BN/EP-4 -> 0.2 W m−1 K−1',
         notes='Baseline comparison vs 3D aerogel scaffold architecture.'),
]
n13, p13 = append_rows(E23, rows_E23, dict(candidate_id='P060', doi=E23['doi'], paper_title=E23['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_c8ra10211b.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='LDPE/BN/epoxy 0.65 is literature comparison (excluded)',
    qc_findings='2 rows; 3D aerogel scaffold architecture; loading not wt%'))

# ===== E24: 10.3390/ijms24098221 (BN / PU — optional matrix) =====
E24 = dict(doi='10.3390/ijms24098221', source_url='https://doi.org/10.3390/ijms24098221',
           paper_title='Fabrication of BN/PU Composite Films with Enhanced Thermal Conductivity via Phase Inversion',
           year=2023)
rows_E24 = [dict(
    matrix_polymer='PU (polyurethane)', curing_agent='',
    filler_material='BN', filler_material_original='BN70/PU (70 wt% BN), unordered',
    filler_shape='platelet', functionalization='None (unmodified BN)',
    filler_loading_wt_pct='70', filler_loading_original_value='70', filler_loading_original_unit='wt%',
    k_composite_W_mK='0.653', k_original_value='0.653', k_original_unit='W/(m·K)',
    measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.17',
    processing_method='Phase inversion (NIPS) or solvent evaporation (SE) methods',
    source_location='Results: BN70/PU unordered -> 0.653 W/(m·K) (281.87% vs pure PU 0.170)',
    notes='PU matrix (optional polymer). BN60/PU = 0.545; BN60/PU-NIPS = 0.319; BN60/PU-SE = 0.425.'),
]
n14, p14 = append_rows(E24, rows_E24, dict(candidate_id='P061', doi=E24['doi'], paper_title=E24['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_ijms24098221.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='BN60 series not extracted as separate rows',
    qc_findings='1 row; PU matrix (optional)'))

print(f'BATCH18: E23={n13} E24={n14} grand={n13+n14}')
