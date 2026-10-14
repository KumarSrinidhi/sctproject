import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E26: 10.3390/polym17111507 (EMC, h-BN+CNT hybrid) =====
E26 = dict(doi='10.3390/polym17111507', source_url='https://doi.org/10.3390/polym17111507',
           paper_title='Enhancing Thermal Conductivity of Epoxy Molding Compounds via CNT-Optimized Interfacial Networks',
           year=2025)
rows_E26 = [dict(
    matrix_polymer='Epoxy molding compound (EMC)', curing_agent='',
    filler_material='BN', filler_material_original='60 wt.% h-BN + 2 wt.% CNTs hybrid filler',
    filler_shape='hybrid', functionalization='CNT co-filler for interfacial thermal resistance reduction',
    filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt% h-BN (+2 wt% CNTs)',
    k_composite_W_mK='1.10', k_original_value='1.10', k_original_unit='W m−1 K−1',
    measurement_method='Thermal conductivity measurement (per paper; twin-screw extruded EMC)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.36',
    processing_method='Twin-screw extrusion of EMC with h-BN + CNT hybrid filler',
    source_location='Results: 60 wt.% h-BN + 2 wt.% CNTs -> λ = 1.10 W m−1 K−1',
    notes='EMC matrix. CNTs reduce ITR. Si3N4+CNT comparisons (1.14) and Al2O3 (1.19) out of primary scope.')
]
n16, p16 = append_rows(E26, rows_E26, dict(candidate_id='P063', doi=E26['doi'], paper_title=E26['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym17111507.txt',
    tables_inspected='Table 4 TC values', figures_inspected='Figure 5',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='Si3N4, Al2O3 rows excluded (non-BN/AlN primary)',
    qc_findings='1 row; EMC matrix; h-BN+CNT hybrid'))

print(f'BATCH20: E26={n16}')
