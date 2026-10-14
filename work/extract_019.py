import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E25: 10.3390/polym16081169 (PS/BN, compression molding) =====
E25 = dict(doi='10.3390/polym16081169', source_url='https://doi.org/10.3390/polym16081169',
           paper_title='High In-Plane Thermal Conductivity of Polystyrene/BN Composites via Cyclic Compression Molding',
           year=2024)
rows_E25 = [
    dict(matrix_polymer='Polystyrene (PS)', curing_agent='',
         filler_material='BN', filler_material_original='PS/BN-C5, BN, 5 molding cycles at 140C 10 MPa',
         filler_shape='platelet', functionalization='None (cyclic compression molding for orientation)',
         filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.6', k_original_value='1.6', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (in-plane, per paper)', k_direction='in-plane',
         value_source='text', confidence='High', k_matrix_W_mK='0.033',
         processing_method='Cyclic compression molding (5 cycles, 140C, 10 MPa) for BN orientation',
         source_location='Results: PS/BN-C5 five molding cycles 140C 10 MPa -> in-plane 1.6 W/m·K',
         notes='PS matrix (optional polymer). Only 10 wt% BN achieves 1.6 W/m·K in-plane via cyclic molding orientation.'),
    dict(matrix_polymer='Polystyrene (PS)', curing_agent='',
         filler_material='BN', filler_material_original='Control PS/BN (no cyclic molding)',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.22', k_original_value='0.22', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.033',
         processing_method='Standard BN dispersion in PS without cyclic molding',
         source_location='Results: control PS/BN (no molding optimization) -> 0.22 W/m·K',
         notes='Baseline vs cyclic compression molding (1.6 W/m·K).')
]
n15, p15 = append_rows(E25, rows_E25, dict(candidate_id='P062', doi=E25['doi'], paper_title=E25['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym16081169.txt',
    tables_inspected='TC tables', figures_inspected='k figures, molding cycles',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='single-cycle values (0.7-1.2) not extracted as separate rows',
    qc_findings='2 rows; PS matrix (optional); cyclic compression molding orientation'))

print(f'BATCH19: E25={n15}')
