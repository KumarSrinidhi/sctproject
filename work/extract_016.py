import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E18: 10.3390/polym11081335 (BNNS / epoxy) =====
E18 = dict(doi='10.3390/polym11081335', source_url='https://doi.org/10.3390/polym11081335',
           paper_title='Epoxy/BN Composites with High Thermal Conductivity and Excellent Electrical Insulation',
           year=2020)
rows_E18 = [
    dict(matrix_polymer='Epoxy', curing_agent='',
         filler_material='BN', filler_material_original='Boron nitride sheets (BNS), 40 wt%',
         filler_shape='platelet', functionalization='None (gravity-mix)',
         filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.66', k_original_value='1.66', k_original_unit='W·m−1·K−1',
         measurement_method='Thermal conductivity measurement (per paper; gravity-mix composites)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.21', measurement_temperature_C='298',
         processing_method='Gravity-mix method for controllable BNS loading (5-40 wt%)',
         source_location='Results: 40 wt% BNS -> 1.66 W·m−1·K−1 at 298 K (765% vs neat epoxy)',
         notes='BNS loading range 5-40 wt%. 298 K (room temperature).'),
    dict(matrix_polymer='Epoxy', curing_agent='',
         filler_material='BN', filler_material_original='Boron nitride sheets (BNS), 40 wt%',
         filler_shape='platelet', functionalization='None (gravity-mix)',
         filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.84', k_original_value='0.84', k_original_unit='W·m−1·K−1',
         measurement_method='Thermal conductivity measurement (per paper; cryogenic)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='', measurement_temperature_C='77',
         processing_method='Gravity-mix method',
         source_location='Results: 40 wt% BNS -> 0.84 W·m−1·K−1 at 77 K',
         notes='Cryogenic (77 K) value for superconducting magnet insulation application.'),
]
n8, p8 = append_rows(E18, rows_E18, dict(candidate_id='P055', doi=E18['doi'], paper_title=E18['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11081335.txt',
    tables_inspected='TC tables', figures_inspected='k vs loading, log-log plot',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='none needed',
    qc_findings='2 rows; 40 wt% BNS at 298 K and 77 K'))

# ===== E19: 10.3390/polym13030456 (PEG/BN PCM — optional matrix) =====
E19 = dict(doi='10.3390/polym13030456', source_url='https://doi.org/10.3390/polym13030456',
           paper_title='Thermal Conductivity Enhancement of Phase Change Material with Boron Nitride via Surface Modification',
           year=2018)
rows_E19 = [
    dict(matrix_polymer='PEG (polyethylene glycol, PCM)', curing_agent='',
         filler_material='BN', filler_material_original='BN, 30 wt% (P-c-BN/PEG, PVA-grafted/crosslinked)',
         filler_shape='platelet', functionalization='PVA grafting + crosslinking',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.89', k_original_value='0.89', k_original_unit='W/mK',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.23',
         processing_method='PVA surface modification + crosslinking of BN in PEG matrix',
         source_location='Results: P-c-BN/PEG at 30 wt% = 0.89 W/mK (286% vs neat PEG 0.23)',
         notes='PEG matrix (PCM, optional polymer). Surface modification improves interfacial adhesion and k.'),
    dict(matrix_polymer='PEG (polyethylene glycol, PCM)', curing_agent='',
         filler_material='BN', filler_material_original='Pristine BN/PEG, 30 wt%',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.61', k_original_value='0.61', k_original_unit='W/mK',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.23',
         processing_method='Pristine BN dispersed in PEG',
         source_location='Results: PEG/BN at 30 wt% = 0.61 W/mK (pristine BN comparison)',
         notes='Baseline vs surface-modified P-c-BN (0.89 W/mK).'),
]
n9, p9 = append_rows(E19, rows_E19, dict(candidate_id='P056', doi=E19['doi'], paper_title=E19['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13030456.txt',
    tables_inspected='thermal tables', figures_inspected='k figures',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='10/20 wt% intermediate values not extracted as separate rows',
    qc_findings='2 rows; PEG PCM matrix (optional); surface-modified vs pristine BN'))

print(f'BATCH16: E18={n8} E19={n9} grand={n8+n9}')
