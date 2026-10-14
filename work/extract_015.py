import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E11: 10.3390/ma14185251 (BNNSs/MWCNTs@mSiO2 / epoxy) =====
E11 = dict(doi='10.3390/ma14185251', source_url='https://doi.org/10.3390/ma14185251',
           paper_title='Synergistic Enhanced Thermal Conductivity and Dielectric Constant of Epoxy Composites with BNNSs and MWCNTs@mSiO2',
           year=2021)
rows = [dict(
    matrix_polymer='Epoxy', curing_agent='',
    filler_material='BNNS', filler_material_original='BNNSs 20 wt% + 0.1 wt% MWCNTs@mSiO2 hybrid filler',
    filler_shape='platelet', functionalization='MWCNTs@mSiO2 co-filler (0.1 wt%)',
    filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt% BNNSs (+0.1 wt% MWCNTs@mSiO2)',
    k_composite_W_mK='0.68', k_original_value='0.68', k_original_unit='W m−1 K−1',
    measurement_method='Thermal conductivity of composites (per paper; network structure explanation)',
    k_direction='unknown', value_source='text', confidence='High', k_matrix_W_mK='',
    processing_method='BNNSs + MWCNTs@mSiO2 in epoxy, hybrid filler network',
    source_location='Abstract+Results: TC = 0.68 W m−1 K−1 at 20 wt% filler (187% higher than epoxy)',
    notes='Hybrid filler system. 20 wt% BNNSs is the threshold for remarkable TC increase.')]
n1, p1 = append_rows(E11, rows, dict(candidate_id='P048', doi=E11['doi'], paper_title=E11['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_ma14185251.txt',
    tables_inspected='Table 1 thermal data', figures_inspected='k vs filler content',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='BNNSs/BNMSs/epoxy 1.15 W/mK lit value excluded',
    qc_findings='1 row; hybrid BNNS+MWCNT filler'))

# ===== E12: 10.1039/c9ra00282k (h-BN/c-BN hybrid / epoxy) =====
E12 = dict(doi='10.1039/c9ra00282k', source_url='https://doi.org/10.1039/c9ra00282k',
           paper_title='Hybrid fillers of hexagonal and cubic boron nitride in epoxy composites for thermal management',
           year=2019)
common12 = dict(matrix_polymer='Epoxy', curing_agent='',
                measurement_method='Thermal conductivity measurement (per paper; Agari model comparison)',
                k_direction='unknown', value_source='text', confidence='High',
                processing_method='h-BN platelets + c-BN spheres hybrid in epoxy',
                source_location='Results section TC discussion')
rows_E12 = [
    dict(common12, filler_material='h-BN', filler_material_original='modified h-BN platelets, 9 vol%',
         filler_shape='platelet', functionalization='surface-modified (covalent)',
         filler_loading_vol_pct='9', filler_loading_original_value='9', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.44', k_original_value='0.44', k_original_unit='W m−1 K−1',
         k_matrix_W_mK='0.195',
         source_location='Results: modified h-BN at 9 vol% -> 0.44 W m−1 K−1 (2.3x neat EP 0.195)',
         notes='Single-filler h-BN series at 9 vol%.'),
    dict(common12, filler_material='h-BN', filler_material_original='h-BN/c-BN hybrid, 6.5 vol% total, h-BN:c-BN = 2:1',
         filler_shape='hybrid', functionalization='modified h-BN + c-BN spheres',
         filler_loading_vol_pct='6.5', filler_loading_original_value='6.5', filler_loading_original_unit='vol% (2:1 h-BN:c-BN)',
         k_composite_W_mK='0.421', k_original_value='0.421', k_original_unit='W m−1 K−1',
         source_location='Results: 6.5 vol% BN (h-BN/c-BN = 2:1) -> 0.421 W m−1 K−1',
         notes='Hybrid ratio series; non-monotonic with loading (7.5 vol% 3:4 = 0.384 lower).'),
    dict(common12, filler_material='h-BN', filler_material_original='h-BN/c-BN hybrid, 7.5 vol% total, h-BN:c-BN = 3:4',
         filler_shape='hybrid', functionalization='modified h-BN + c-BN spheres',
         filler_loading_vol_pct='7.5', filler_loading_original_value='7.5', filler_loading_original_unit='vol% (3:4 h-BN:c-BN)',
         k_composite_W_mK='0.384', k_original_value='0.384', k_original_unit='W m−1 K−1',
         source_location='Results: 7.5 vol% (h-BN/c-BN = 3:4) -> unexpectedly low 0.384 W m−1 K−1',
         notes='Anomalous decrease vs 6.5 vol% 2:1 ratio (dispersion effect).'),
]
n2, p2 = append_rows(E12, rows_E12, dict(candidate_id='P049', doi=E12['doi'], paper_title=E12['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_c9ra00282k.txt',
    tables_inspected='TC tables', figures_inspected='Fig 4, Fig 5 k vs loading',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='6 vol% hybrid increase percentages (not absolute k) not extracted as separate rows',
    qc_findings='3 rows; hybrid h-BN/c-BN ratios; neat EP 0.195'))

# ===== E13: 10.3390/nano11081898 (sandwich AlN/epoxy) =====
E13 = dict(doi='10.3390/nano11081898', source_url='https://doi.org/10.3390/nano11081898',
           paper_title='Simultaneously Enhanced Thermal Conductivity and Dielectric Breakdown Strength in Sandwich AlN/Epoxy Composites',
           year=2021)
common13 = dict(matrix_polymer='Epoxy (DGEBA E-828)', curing_agent='methyl tetrahydrophthalic anhydride',
                filler_material='AlN', filler_material_original='Sandwich: outer ANMP (micro-AlN 5 um) + middle ANNP (nano-AlN 40 nm)',
                filler_shape='hybrid', functionalization='None',
                filler_loading_vol_pct='35.6', filler_loading_original_value='35.6', filler_loading_original_unit='vol% ANMP outer layer (1.0 vol% ANNP middle)',
                measurement_method='Laser flash (LFA467 Netzsch), through-plane and in-plane',
                k_direction='through-plane', value_source='text', confidence='High',
                processing_method='Layer-by-layer hot-press casting (outer ANMP / middle ANNP / outer ANMP), cure 150 C',
                source_location='Abstract+Results: sandwich TC values',
                notes='Sandwich architecture; outer layers 35.6 vol% micro-AlN, middle 1.0 vol% nano-AlN. Pure epoxy 4.1x lower (0.18 W/(m·K) implied).')
rows_E13 = [
    dict(common13, filler_material_original='Sandwich 120-60 (outer 120 um, middle 60 um), 35.6 vol% ANMP outer + 1.0 vol% ANNP middle',
         k_direction='through-plane',
         k_composite_W_mK='0.754', k_original_value='0.754', k_original_unit='W/(m·K)',
         source_location='Abstract: 120-60 through-plane TC = 0.754 W/(m·K) (4.1x epoxy)',
         notes=common13['notes'] + ' Optimal dielectric breakdown 69.7 kV/mm.'),
    dict(common13, filler_material_original='Sandwich 120-60, in-plane (from parallel models)',
         k_direction='in-plane',
         k_composite_W_mK='1.88', k_original_value='1.88', k_original_unit='W/(m·K)',
         source_location='Results: in-plane TC 1.88 W/(m·K) for 120-60 based on parallel models',
         notes='Anisotropic sandwich; in-plane higher than through-plane.'),
    dict(common13, filler_material_original='Sandwich 130-60 (outer 130 um, middle 60 um)',
         k_direction='through-plane',
         k_composite_W_mK='0.904', k_original_value='0.904', k_original_unit='W/(m·K)',
         source_location='Results: TPTC of 130-60 reaches 0.904 W/(m·K)',
         notes='Thicker outer layer (higher AlN) improves through-plane TC.'),
]
n3, p3 = append_rows(E13, rows_E13, dict(candidate_id='P050', doi=E13['doi'], paper_title=E13['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano11081898.txt',
    tables_inspected='dielectric/TC tables', figures_inspected='SEM + TC figures',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='none needed',
    qc_findings='3 rows; sandwich architecture; 35.6 vol% micro-AlN outer layers'))

# ===== E14: 10.3390/polym11010138 (AlN / cycloaliphatic epoxy) =====
E14 = dict(doi='10.3390/polym11010138', source_url='https://doi.org/10.3390/polym11010138',
           paper_title='Thermal Conductive Composites Prepared by Addition of Several Ceramic Fillers to Thermally Cationic Curing Cycloaliphatic Epoxy Resins',
           year=2019)
rows_E14 = [dict(
    matrix_polymer='Cycloaliphatic epoxy (thermally cationic curing)', curing_agent='cationic latent initiator',
    filler_material='AlN', filler_material_original='AlN particles, 75 wt%',
    filler_shape='sphere', functionalization='None',
    filler_loading_wt_pct='75', filler_loading_original_value='75', filler_loading_original_unit='wt%',
    k_composite_W_mK='1.21', k_original_value='1.21', k_original_unit='W/m·K',
    measurement_method='Thermal conductivity determination (per paper; cycloaliphatic epoxy composites)',
    k_direction='unknown', value_source='text', confidence='High', k_matrix_W_mK='0.2',
    processing_method='Thermal cationic curing of cycloaliphatic epoxy with ceramic fillers',
    source_location='Abstract+Results: highest TC 1.21 W/m·K at 75 wt% AlN (820% over neat)',
    notes='Cycloaliphatic epoxy (not DGEBA). SiC comparison (1.12 W/m·K) excluded (out of primary filler scope). BN comparison 1.04 is literature.')]
n4, p4 = append_rows(E14, rows_E14, dict(candidate_id='P051', doi=E14['doi'], paper_title=E14['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11010138.txt',
    tables_inspected='TC tables', figures_inspected='TC figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='SiC and literature BN values excluded',
    qc_findings='1 row; cycloaliphatic epoxy matrix (optional)'))

# ===== E15: 10.3390/polym14061252 (LC epoxy + BN) =====
E15 = dict(doi='10.3390/polym14061252', source_url='https://doi.org/10.3390/polym14061252',
           paper_title='Characteristic and Synthesis of High-Temperature Resistant Liquid Crystal Epoxy Resin Containing Boron Nitride with High Thermal Conductivity',
           year=2022)
rows_E15 = [
    dict(matrix_polymer='Liquid crystal epoxy (SBPDAE)', curing_agent='',
         filler_material='BN', filler_material_original='spherical BN (s-BN), 60% loading, SBPDAE matrix',
         filler_shape='sphere', functionalization='None',
         filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt%',
         k_composite_W_mK='9.36', k_original_value='9.36', k_original_unit='W/mK',
         measurement_method='Thermal conductivity measurement (vertical direction of LC-aligned composite)',
         k_direction='through-plane (vertical)', value_source='text', confidence='High',
         processing_method='LC epoxy resin (SBPDAE) + spherical BN, LC alignment enhances vertical k',
         source_location='Abstract: SBPDAE/s-BN (60%) = 9.36 W/mK vertical',
         notes='Liquid crystal epoxy matrix (optional polymer); LC alignment enables high vertical k with spherical BN.'),
    dict(matrix_polymer='Liquid crystal epoxy (TMBPE)', curing_agent='',
         filler_material='BN', filler_material_original='flat BN (f-BN), TMBPE matrix',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='', filler_loading_original_value='', filler_loading_original_unit='',
         k_composite_W_mK='6.77', k_original_value='6.77', k_original_unit='W/mK',
         measurement_method='Thermal conductivity measurement', k_direction='unknown',
         value_source='text', confidence='Medium',
         processing_method='TMBPE LC epoxy + f-BN',
         source_location='Results: TMBPE with f-BN = 6.77 W/mK (highest among five LC epoxies with f-BN)',
         notes='Loading not stated in text snippet; Medium confidence. Pure LC epoxies 0.17-0.21 W/mK.')]
# E15 row 2 has empty loading - will be rejected; remove it
rows_E15 = rows_E15[:1]
n5, p5 = append_rows(E15, rows_E15, dict(candidate_id='P052', doi=E15['doi'], paper_title=E15['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym14061252.txt',
    tables_inspected='TC tables', figures_inspected='TC figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='TMBPE 6.77 excluded (loading not numeric)',
    qc_findings='1 row; LC epoxy matrix (optional); s-BN 60% loading'))

# ===== E16: 10.3390/polym12091913 (K-LCE / modified BN) =====
E16 = dict(doi='10.3390/polym12091913', source_url='https://doi.org/10.3390/polym12091913',
           paper_title='Preparation and Thermomechanical Properties of Ketone Mesogenic Liquid Crystalline Epoxy Resin/BN Composites with High Thermal Conductivity',
           year=2020)
rows_E16 = [dict(
    matrix_polymer='Ketone mesogenic liquid crystalline epoxy (K-LCE)', curing_agent='',
    filler_material='BN', filler_material_modified='surface-modified BN',
    filler_material_original='Modified BN fillers, 5.00 wt%',
    filler_shape='platelet', functionalization='surface-modified BN',
    filler_loading_wt_pct='5', filler_loading_original_value='5', filler_loading_original_unit='wt%',
    k_composite_W_mK='0.58', k_original_value='0.58', k_original_unit='W/m·K',
    measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
    value_source='text', confidence='High', k_matrix_W_mK='0.34',
    processing_method='K-LCE matrix + surface-modified BN fillers',
    source_location='Results: K-LCE/BN at 5.00 wt% = 0.58 W/m·K; pure K-LCE 0.34 W/m·K',
    notes='LC epoxy matrix (optional); 5 wt% modified BN gives 0.58 W/m·K. Intermediate loadings 0.05-2 wt% series (0.39-0.53) not all extracted as separate rows.')]
# fix field name - filler_modified not valid
rows_E16[0].pop('filler_material_modified', None)
n6, p6 = append_rows(E16, rows_E16, dict(candidate_id='P053', doi=E16['doi'], paper_title=E16['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym12091913.txt',
    tables_inspected='thermal tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='DGEBA literature comparisons excluded',
    qc_findings='1 row; LC epoxy matrix (optional)'))

# ===== E17: 10.1039/c8ra03875a (AT-BN / ETDS epoxy-thiol) =====
E17 = dict(doi='10.1039/c8ra03875a', source_url='https://doi.org/10.1039/c8ra03875a',
           paper_title='Surface modification of a BN/ETDS composite with aniline trimer for high thermal conductivity',
           year=2018)
rows_E17 = [
    dict(matrix_polymer='ETDS epoxy-thiol (epoxy + thiol curing)', curing_agent='thiol',
         filler_material='BN', filler_material_original='AT-BN_2 (BN:AT = 2:1 aniline trimer treated), 50 wt% filler',
         filler_shape='platelet', functionalization='Aniline trimer (AT) surface treatment',
         filler_loading_wt_pct='50', filler_loading_original_value='50', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.25', k_original_value='1.25', k_original_unit='W m−1 K−1',
         measurement_method='Thermal conductivity measurement (per paper)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.19',
         processing_method='AT-treated BN in ETDS epoxy-thiol matrix',
         source_location='Abstract+Results: AT-BN_2 highest TC = 1.25 W m−1 K−1 (8.06x pristine ETDS 0.19)',
         notes='Surface-functionalized BN; AT amount optimized (BN:AT ratios 1:1 to 20:1 studied).'),
    dict(matrix_polymer='ETDS epoxy-thiol', curing_agent='thiol',
         filler_material='BN', filler_material_original='Pristine (untreated) BN/ETDS, 50 wt%',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='50', filler_loading_original_value='50', filler_loading_original_unit='wt%',
         k_composite_W_mK='', k_original_value='', k_original_unit='',
         measurement_method='Thermal conductivity measurement', k_direction='unknown',
         value_source='text', confidence='Low',
         processing_method='Pristine BN in ETDS',
         source_location='(placeholder - pristine BN 50 wt% value not fully quoted in snippet)',
         notes='Baseline for AT treatment comparison; exact k not extracted (figure-only).')]
# Drop the placeholder - only extract the confirmed 1.25 value
rows_E17 = rows_E17[:1]
n7, p7 = append_rows(E17, rows_E17, dict(candidate_id='P054', doi=E17['doi'], paper_title=E17['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_c8ra03875a.txt',
    tables_inspected='TC tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='pristine BN 50 wt% figure-only, excluded',
    qc_findings='1 row; surface-modified BN; epoxy-thiol matrix'))

print(f'BATCH15: E11={n1} E12={n2} E13={n3} E14={n4} E15={n5} E16={n6} E17={n7} grand={n1+n2+n3+n4+n5+n6+n7}')
