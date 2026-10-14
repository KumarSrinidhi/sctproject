import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== B1: 10.3390/polym11040597 (BN + Al2O3 / epoxy film) =====
B1 = dict(doi='10.3390/polym11040597', source_url='https://doi.org/10.3390/polym11040597',
          paper_title='Rheological Properties and Thermal Conductivity of Epoxy Resins Filled with a Mixture of Alumina and Boron Nitride',
          year=2019)
common_B1 = dict(matrix_polymer='Epoxy resin (EP)', curing_agent='',
                 filler_material='Al2O3/BN hybrid', filler_shape='other',
                 functionalization='None',
                 measurement_method='LFA (Netzsch LFA 447) perpendicular to film plane, RT; k = alpha x rho x Cp',
                 k_direction='through-plane', measurement_temperature_C='25',
                 value_source='text', confidence='High', k_matrix_W_mK='',
                 processing_method='Al2O3 (DAB1800 grade) + BN platelets in epoxy, cast as film')
rows_B1 = [
    dict(common_B1, filler_material_original='Al2O3 (DAB1800) + BN platelets, sample BN50DAB1800',
         filler_loading_vol_pct='3.63', filler_loading_original_value='3.63', filler_loading_original_unit='vol% (BN portion; total filler 73.72 vol%)',
         k_composite_W_mK='3.35', k_original_value='3.35', k_original_unit='W/(m·K)',
         source_location='Results text: 3.63 vol% (BN50DAB1800) -> 3.35 W/(m·K)',
         notes='BN 3.63 vol%, total filler ~73.72 vol% (Al2O3-dominated).'),
    dict(common_B1, filler_material_original='Al2O3 (DAB1800) + BN platelets, sample BN75DAB1800',
         filler_loading_vol_pct='5.32', filler_loading_original_value='5.32', filler_loading_original_unit='vol% (BN portion; total filler 74.14 vol%)',
         k_composite_W_mK='4.44', k_original_value='4.44', k_original_unit='W/(m·K)',
         source_location='Results text: 5.32 vol% (BN75DAB1800) -> 4.44 W/(m·K); optimum 5.3 vol% BN, max 4.4',
         notes='Optimal BN content, max k of series. Total filler ~74.14 vol%.'),
    dict(common_B1, filler_material_original='Al2O3 (DAB1800) + BN platelets, sample BN90DAB1800',
         filler_loading_vol_pct='6.32', filler_loading_original_value='6.32', filler_loading_original_unit='vol% (BN portion; total filler 74.47 vol%)',
         k_composite_W_mK='4.05', k_original_value='4.05', k_original_unit='W/(m·K)',
         source_location='Results text: 6.32 vol% (BN90DAB1800) -> 4.05 W/(m·K) (drop attributed to BN reorientation)',
         notes='Total filler ~74.47 vol%; k drops vs 5.32 vol% BN due to orientation change.'),
]
n1, p1 = append_rows(B1, rows_B1, dict(candidate_id='P030', doi=B1['doi'], paper_title=B1['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11040597.txt',
    tables_inspected='rheology tables', figures_inspected='k discussion in text (Fig 4b)',
    candidate_measurements=3, unit_conversions='none', duplicate_checks='Al2O3-only film value not numerically stated (only 1.6x ratio) - excluded',
    qc_findings='3 rows; loading recorded as BN vol% with total filler in notes'))

# ===== B2: 10.1038/s41598-018-19945-3 (BNNS / polyimide film) =====
B2 = dict(doi='10.1038/s41598-018-19945-3', source_url='https://doi.org/10.1038/s41598-018-19945-3',
          paper_title='In-plane and out-of-plane thermal conductivity of polyimide composites with boron nitride nanosheets',
          year=2018)
common_B2 = dict(matrix_polymer='Polyimide (PI)', curing_agent='',
                 filler_material='BNNS', filler_material_original='BNNSs (boron nitride nanosheets)',
                 filler_shape='nanosheet', functionalization='None',
                 value_source='text', confidence='High', k_matrix_W_mK='0.25',
                 measurement_method='Thermal conductivity of PI/BNNS films (Fig 6a in-plane, Fig 6b out-of-plane)')
rows_B2 = []
for wt, kip in [(1, 1.83), (3, 2.22), (5, 2.76), (7, 2.95)]:
    r = dict(common_B2)
    r.update(filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt%',
             k_composite_W_mK=str(kip), k_original_value=str(kip), k_original_unit='W/mK',
             k_direction='in-plane',
             source_location=f'Fig 6a quoted in text: in-plane at {wt} wt% = {kip} W/mK',
             notes=f'PI/BNNS {wt} wt% in-plane. Optional matrix: polyimide (not epoxy). Neat PI 0.25 W/mK both directions.')
    rows_B2.append(r)
for wt, kop in [(1, 0.26), (3, 0.33), (5, 0.36), (7, 0.44)]:
    r = dict(common_B2)
    r.update(filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt%',
             k_composite_W_mK=str(kop), k_original_value=str(kop), k_original_unit='W/mK',
             k_direction='through-plane (out-of-plane)',
             source_location=f'Fig 6b quoted in text: out-of-plane at {wt} wt% = {kop} W/mK',
             notes=f'PI/BNNS {wt} wt% out-of-plane (paired with in-plane row at same loading).')
    rows_B2.append(r)
n2, p2 = append_rows(B2, rows_B2, dict(candidate_id='P031', doi=B2['doi'], paper_title=B2['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1038_s41598-018-19945-3.txt',
    tables_inspected='none with k', figures_inspected='Fig 6a/6b (values enumerated in text)',
    candidate_measurements=8, unit_conversions='none', duplicate_checks='neat PI 0.25 kept as k_matrix',
    qc_findings='8 rows (4 loadings x 2 directions); optional polyimide matrix'))

# ===== B3: 10.3390/polym11121990 (AlN + magnetically aligned Ni / epoxy) =====
B3 = dict(doi='10.3390/polym11121990', source_url='https://doi.org/10.3390/polym11121990',
          paper_title='Magnetically aligned nickel powder in AlN/epoxy composites with enhanced thermal conductivity',
          year=2019)
common_B3 = dict(matrix_polymer='Epoxy resin', curing_agent='',
                 filler_material='AlN', filler_material_original='AlN (30 vol%, 1 um) + Ni powder (2 vol%)',
                 filler_shape='particle', functionalization='None',
                 filler_loading_vol_pct='32', filler_loading_original_value='30 AlN + 2 Ni',
                 filler_loading_original_unit='vol%',
                 filler_alignment='Ni chains aligned by vertical magnetic field',
                 measurement_method='Thermal conductivity measurement (per text; values vs pure epoxy 0.2 W/mK)',
                 k_direction='through-plane (vertical alignment)', value_source='text', confidence='High',
                 k_matrix_W_mK='0.2')
rows_B3 = [
    dict(common_B3, filler_material_original='AlN only (30 vol%, 1 um)',
         filler_loading_vol_pct='30', filler_loading_original_value='30', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.933', k_original_value='0.933', k_original_unit='W/mK',
         source_location='Text: composites filled with only 30 vol% 1 um-AlN = 0.933 W/mK',
         notes='Control: AlN-only at 30 vol%. Pure epoxy 0.2 W/mK.'),
    dict(common_B3, filler_material_original='AlN 30 vol% + Ni 50 nm 2 vol%, magnetic alignment',
         k_composite_W_mK='1.401', k_original_value='1.401', k_original_unit='W/mK',
         source_location='Fig 5 discussion: Ni 50 nm -> 1.401 W/mK',
         notes='Ni particle size series (50 nm) at 30 vol% AlN + 2 vol% Ni, magnetic field aligned.'),
    dict(common_B3, filler_material_original='AlN 30 vol% + Ni 1 um 2 vol%, magnetic alignment',
         k_composite_W_mK='1.474', k_original_value='1.474', k_original_unit='W/mK',
         source_location='Text + Fig 5: Ni 1 um -> 1.474 W/mK (max, +737% vs pure EP, +58% vs AlN-only)',
         notes='Optimal Ni size 1 um.'),
    dict(common_B3, filler_material_original='AlN 30 vol% + Ni 10 um 2 vol%, magnetic alignment',
         k_composite_W_mK='1.445', k_original_value='1.445', k_original_unit='W/mK',
         source_location='Fig 5 discussion: Ni 10 um -> 1.445 W/mK',
         notes='Ni particle size series (10 um).'),
]
n3, p3 = append_rows(B3, rows_B3, dict(candidate_id='P032', doi=B3['doi'], paper_title=B3['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11121990.txt',
    tables_inspected='filler property tables', figures_inspected='Fig 5 (Ni size series, values in text)',
    candidate_measurements=4, unit_conversions='none', duplicate_checks='1.182 (nano-Al2O3) and 1.21 (AlN+MWCNT) are literature refs - excluded',
    qc_findings='4 rows; metallic Ni secondary filler; 30vol% AlN control row included'))

print(f'BATCH9 appended: B1={n1} B2={n2} B3={n3} grand={n1+n2+n3}')
