import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E7: 10.3390/ma10121442 (AlN porous skeleton / epoxy) =====
E7 = dict(doi='10.3390/ma10121442', source_url='https://doi.org/10.3390/ma10121442',
          paper_title='Development of AlN/Epoxy Composites with Enhanced Thermal Conductivity',
          year=2017)
rows = []
for frac, kval, note in [
    ('19.7', '7.5', 'AlN skeleton 19.7 vol% (75.3% porosity ceramic infiltrated)'),
    ('27.9', '19.0', 'AlN skeleton 27.9 vol% (72.1% porosity ceramic); highest k'),
]:
    rows.append(dict(
        matrix_polymer='Epoxy', curing_agent='',
        filler_material='AlN', filler_material_original=f'AlN porous ceramic skeleton (infiltrated epoxy), {frac} vol% AlN network',
        filler_shape='other', functionalization='None',
        filler_alignment='continuous 3D skeleton (porous ceramic preform)',
        filler_loading_vol_pct=frac, filler_loading_original_value=frac, filler_loading_original_unit='vol% AlN skeleton',
        k_composite_W_mK=kval, k_original_value=kval, k_original_unit='W/(m·K)',
        measurement_method='Thermal conductivity of AlN/epoxy composites (per paper; porous ceramic preform infiltration)',
        k_direction='unknown', value_source='text', confidence='High', k_matrix_W_mK='0.2',
        processing_method='Epoxy infiltration into AlN porous ceramic (preform), porosity-controlled skeleton',
        source_location='Results: TC increased from 7.5 to 19.0 W/(m·K) with AlN skeleton fraction 19.7% to 27.9%; pure epoxy 0.2 W/(m·K)',
        notes='Continuous AlN skeleton (not particulate filler); two orders of magnitude above pure epoxy.'))
n1, p1 = append_rows(E7, rows, dict(candidate_id='P044', doi=E7['doi'], paper_title=E7['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_ma10121442.txt',
    tables_inspected='mechanical tables', figures_inspected='TC figures',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='none needed',
    qc_findings='2 rows; continuous ceramic skeleton (not particulate); high k'))

# ===== E8: 10.3390/polym17111429 (BN/epoxy + AC field) =====
E8 = dict(doi='10.3390/polym17111429', source_url='https://doi.org/10.3390/polym17111429',
          paper_title='High Frequency Electric-Field-Assisted Preparation of BN/Epoxy Resin Composites with Excellent Thermal Conductivity',
          year=2025)
common = dict(matrix_polymer='Epoxy', curing_agent='',
              filler_material='BN', filler_shape='platelet', functionalization='None',
              filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt% (BN in epoxy mixture)',
              measurement_method='Thermal conductivity testing (per paper; BN/EP composites prepared with AC electric field)',
              k_direction='out-of-plane', value_source='text', confidence='High',
              processing_method='BN/epoxy mixed, high-frequency AC electric field applied during processing to align BN',
              source_location='Results: TC vs applied field strength',
              notes='30 wt% BN throughout; pure epoxy 0.23 W/(m·K). High-frequency AC field aligns BN.')
rows_E8 = [
    dict(common, filler_material_original='BN 30 wt%, no electric field (0&BN-EP)',
         filler_alignment='random',
         k_composite_W_mK='0.58', k_original_value='0.58', k_original_unit='W/(m·K)',
         source_location='Results: 0&BN-EP = 0.58 W/(m·K) (2.52x epoxy)',
         notes=common['notes'] + ' Baseline no field.'),
    dict(common, filler_material_original='BN 30 wt%, 30 V/mm AC field',
         filler_alignment='field-aligned',
         k_composite_W_mK='0.95', k_original_value='0.95', k_original_unit='W/(m·K)',
         source_location='Results: 30 V/mm -> TC = 0.95 W/(m·K) (also optimum for mechanical/breakdown)',
         notes=common['notes']),
    dict(common, filler_material_original='BN 30 wt%, 60 V/mm AC field',
         filler_alignment='field-aligned',
         k_composite_W_mK='1.03', k_original_value='1.03', k_original_unit='W/(m·K)',
         source_location='Results: 60 V/mm -> 60&BN-EP = 1.03 W/(m·K) (1.77x no-field)',
         notes=common['notes'] + ' Highest field tested; TC max at 60 V/mm.'),
]
n2, p2 = append_rows(E8, rows_E8, dict(candidate_id='P045', doi=E8['doi'], paper_title=E8['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym17111429.txt',
    tables_inspected='property tables', figures_inspected='TC figures',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='literature values (1.52, 0.95 from other refs) excluded',
    qc_findings='3 rows at 30 wt% BN; field strength is the variable'))

# ===== E9: 10.3390/ma18215011 (BN-AlN potting adhesive) =====
E9 = dict(doi='10.3390/ma18215011', source_url='https://doi.org/10.3390/ma18215011',
          paper_title='Manufacturing and Application of Low-Cost Potting Adhesive with High Thermal Conductivity',
          year=2025)
rows_E9 = [
    dict(matrix_polymer='Epoxy-based potting adhesive (381-4DZ commercial, epoxy resin)',
         curing_agent='',
         filler_material='AlN', filler_material_original='AlN spherical (1 um and 10 um), single filler (AlN only)',
         filler_shape='sphere', functionalization='None',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.052', k_original_value='1.052', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='AlN powders (1 um + 10 um) mixed into 381-4DZ adhesive, mechanically stirred',
         source_location='Results: 30 wt% AlN = 1.052 W/m·K (25.2% lower than BN-AlN)',
         notes='Baseline single-filler system for comparison; multi-scale AlN.'),
    dict(matrix_polymer='Epoxy-based potting adhesive (381-4DZ)',
         curing_agent='',
         filler_material='BN', filler_material_original='Functionalized h-BN (1 um) + AlN hybrid, h-BN:AlN = 4:1, 25 wt% total',
         filler_shape='hybrid', functionalization='KH-550 silane coupling agent',
         filler_loading_wt_pct='25', filler_loading_original_value='25', filler_loading_original_unit='wt% (4:1 h-BN:AlN)',
         k_composite_W_mK='1.182', k_original_value='1.182', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High',
         processing_method='KH-550 functionalized h-BN (1 um) + multi-scale AlN (1+10 um) into 381-4DZ, mechanical stirring',
         source_location='Abstract+Results: BN-AlN = 1.182 W/m·K at 25 wt%, BN:AlN 4:1, 48.7% over commercial adhesive 381-4DZ',
         notes='Optimal loading (hardness constraint). Multi-scale 0D+2D filler network.'),
    dict(matrix_polymer='Epoxy-based potting adhesive (381-4DZ)',
         curing_agent='',
         filler_material='BN', filler_material_original='h-BN (1 um) + AlN hybrid, h-BN:AlN = 4:1, 30 wt% total',
         filler_shape='hybrid', functionalization='KH-550',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt% (4:1 h-BN:AlN)',
         k_composite_W_mK='1.278', k_original_value='1.278', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High',
         processing_method='As above, 30 wt% loading',
         source_location='Results: at 30 wt%, BN-AlN = 1.278 W/m·K; 25.2% higher than AlN-only',
         notes='Higher loading gives higher k but exceeds hardness requirement for potting.'),
]
n3, p3 = append_rows(E9, rows_E9, dict(candidate_id='P046', doi=E9['doi'], paper_title=E9['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_ma18215011.txt',
    tables_inspected='orthogonal design tables', figures_inspected='TC figures',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='literature comparison values excluded',
    qc_findings='3 rows; matrix is commercial epoxy potting adhesive 381-4DZ'))

# ===== E10: 10.3390/polym15061552 (cast hBN/epoxy) =====
E10 = dict(doi='10.3390/polym15061552', source_url='https://doi.org/10.3390/polym15061552',
           paper_title='Thermal Conductivity and Mechanical Properties of Polymer Composites with Hexagonal Boron Nitride—A Comparison of Three Processing Methods: Injection Moulding, Powder Bed Fusion and Casting',
           year=2023)
rows_E10 = [
    dict(matrix_polymer='Epoxy (bisphenol-F epoxy 35 wt% + diluent 35 wt% + curing agent 30 wt%)',
         curing_agent='curing agent 30 wt%',
         filler_material='h-BN', filler_material_original='h-BN platelets, ~20 um, 55 wt%',
         filler_shape='platelet', functionalization='None',
         filler_mean_size_um='20',
         filler_loading_wt_pct='55', filler_loading_original_value='55', filler_loading_original_unit='wt% (~28 vol%)',
         k_composite_W_mK='2.0', k_original_value='2.0', k_original_unit='W/m·K',
         measurement_method='Transient laser flash analysis (LFA), k = alpha x Cp x rho; 2 mm specimens',
         k_direction='unknown', value_source='text', confidence='High',
         processing_method='Vacuum mixing, cast into Teflon mould, cure 150 C 18 h',
         source_location='Results/Discussion: highest cast hBN/epoxy = 2.0 W/m·K at 55 wt% (~28 vol%) hBN (~20 um)',
         notes='Casting route; pure epoxy 14x lower (~0.14 W/m·K implied, not quoted numerically). Intermediate loadings figure-only. This is the highest-loading cast sample.'),
    dict(matrix_polymer='Epoxy (same resin system)',
         curing_agent='curing agent 30 wt%',
         filler_material='h-BN', filler_material_original='h-BN platelets, ~20 um, 55 wt% (cast)',
         filler_shape='platelet', functionalization='None',
         filler_mean_size_um='20',
         filler_loading_wt_pct='55', filler_loading_original_value='55', filler_loading_original_unit='wt%',
         k_composite_W_mK='2.0', k_original_value='2.0', k_original_unit='W/m·K',
         measurement_method='LFA, room temperature reference', k_direction='unknown',
         value_source='text', confidence='High',
         processing_method='Vacuum mixing + cast + 150 C 18 h cure',
         source_location='Results: cast hBN/epoxy 55 wt% = 2.0 W/m·K (duplicate of highest cast; included for completeness)',
         notes='Note: Table 1 in this paper cites literature values (21.3, 5.27 etc.) for other systems — those are excluded as not this study.'),
]
n4, p4 = append_rows(E10, rows_E10[:1], dict(candidate_id='P047', doi=E10['doi'], paper_title=E10['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym15061552.txt',
    tables_inspected='Table 1 lit comparisons', figures_inspected='Fig 3 cast k vs T, Fig 4',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='Table 1 lit values (21.3, 7, 5.27, 17.5, etc.) excluded as literature; only cast 55 wt% own data extracted',
    qc_findings='1 row from cast series; temperature-dependent k in Fig 4 (not digitized)'))

print(f'BATCH14: E7={n1} E8={n2} E9={n3} E10={n4} grand={n1+n2+n3+n4}')
