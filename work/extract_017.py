import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E20: 10.3390/nano15120936 (h-BN / epoxy, magnetic field) =====
E20 = dict(doi='10.3390/nano15120936', source_url='https://doi.org/10.3390/nano15120936',
           paper_title='Preparation of High Thermal Conductivity Epoxy Composites with Hexagonal Boron Nitride via Magnetic Field-Assisted Curing',
           year=2025)
rows_E20 = [
    dict(matrix_polymer='Epoxy', curing_agent='',
         filler_material='BN', filler_material_original='Hexagonal boron nitride (h-BN), 10 wt%',
         filler_shape='platelet', functionalization='Magnetic field-assisted curing',
         filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.58', k_original_value='0.58', k_original_unit='Wm−1K−1',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.2',
         processing_method='Magnetic field-assisted curing for BN alignment',
         source_location='Results: 10 wt% h-BN -> 0.58 Wm−1K−1 (field-assisted)',
         notes='Magnetic field-assisted curing improves BN alignment and k.'),
    dict(matrix_polymer='Epoxy', curing_agent='',
         filler_material='BN', filler_material_original='Hexagonal boron nitride (h-BN), 25 wt%',
         filler_shape='platelet', functionalization='Magnetic field-assisted curing',
         filler_loading_wt_pct='25', filler_loading_original_value='25', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.44', k_original_value='1.44', k_original_unit='Wm−1K−1',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.2',
         processing_method='Magnetic field-assisted curing for BN alignment',
         source_location='Results: 25 wt% h-BN -> 1.44 Wm−1K−1 (field-assisted)',
         notes='Highest loading in field-assisted series (10-25 wt%).'),
]
n10, p10 = append_rows(E20, rows_E20, dict(candidate_id='P057', doi=E20['doi'], paper_title=E20['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano15120936.txt',
    tables_inspected='TC tables', figures_inspected='k vs loading figures',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='intermediate 5,15,20 wt% values not extracted as separate rows',
    qc_findings='2 rows; magnetic field-assisted curing method'))

# ===== E21: 10.3390/polym18050648 (Al2O3+BN trimodal / epoxy) =====
E21 = dict(doi='10.3390/polym18050648', source_url='https://doi.org/10.3390/polym18050648',
           paper_title='Tailoring Flame-Retardant and Thermal Conductive Properties of Epoxy Composites with Multimodal Ceramic Fillers',
           year=2026)
rows_E21 = [dict(
    matrix_polymer='Epoxy', curing_agent='',
    filler_material='AlN', filler_material_original='Trimodal composite filler: Al2O3 + BN (total 40 wt%, BN fraction 7.5 wt%)',
    filler_shape='hybrid', functionalization='None',
    filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt% total (7.5 wt% BN + Al2O3)',
    k_composite_W_mK='1.64', k_original_value='1.64', k_original_unit='W/m∙K',
    measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.18',
    processing_method='Trimodal ceramic filler (Al2O3 + BN) in epoxy/BZ matrix',
    source_location='Results: trimodal Al2O3+BN at 40 wt% total, 7.5 wt% BN fraction -> highest TC 1.64 W/m∙K',
    notes='Bimodal Al2O3 40 wt% -> 1.22; MgO 40 wt% -> 1.29; ATH 40 wt% -> 1.0. BN fraction optimized at 7.5 wt% of total.'),
]
n11, p11 = append_rows(E21, rows_E21, dict(candidate_id='P058', doi=E21['doi'], paper_title=E21['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym18050648.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='Al2O3/MgO/ATH bimodal excluded (non-BN primary)',
    qc_findings='1 row; trimodal Al2O3+BN hybrid in epoxy'))

# ===== E22: 10.1007/s40820-023-01163-w (F-CB/BN/CEP coating) =====
E22 = dict(doi='10.1007/s40820-023-01163-w', source_url='https://doi.org/10.1007/s40820-023-01163-w',
           paper_title='Preparation of Highly Thermally Conductive and Anticorrosive Multifunctional Coatings for Heat-Conducting Protection',
           year=2023)
rows_E22 = [dict(
    matrix_polymer='CEP (curing-agent-functionalized epoxy coating)', curing_agent='F-CB (curing agent + BN surface modifier)',
    filler_material='BN', filler_material_original='F-CB/CEP coating, 50 wt% BN (functionalized with curing agent)',
    filler_shape='platelet', functionalization='F-CB (cation-pi interaction: curing agent as BN surface modifier)',
    filler_loading_wt_pct='50', filler_loading_original_value='50', filler_loading_original_unit='wt%',
    k_composite_W_mK='4.29', k_original_value='4.29', k_original_unit='W m−1 K−1',
    measurement_method='Thermal conductivity measurement (per paper; coating TC)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.22',
    processing_method='F-CB (curing agent + BN modifier) in epoxy coating, corrosion-inhibitive',
    source_location='Abstract+Results: F-CB/CEP coating TC = 4.29 W m−1 K−1 at 50 wt% BN',
    notes='Coating matrix (epoxy-based, corrosion-resistant). BN/DEP 50 wt% = 2.51; BN/CEP 50 wt% = 3.95 (comparators). Pure epoxy coating k = 0.22.'),
]
n12, p12 = append_rows(E22, rows_E22, dict(candidate_id='P059', doi=E22['doi'], paper_title=E22['paper_title'],
    date_processed='2026-10-13', access_result='EPMC/Unpaywall (Springer OA)',
    files_inspected='work/fulltext/10.1007_s40820-023-01163-w.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='20 wt% BN values (0.76-0.84) not extracted as separate rows',
    qc_findings='1 row; coating matrix (optional polymer); surface-functionalized BN'))

print(f'BATCH17: E20={n10} E21={n11} E22={n12} grand={n10+n11+n12}')
