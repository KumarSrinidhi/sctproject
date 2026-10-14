import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== M: 10.1039/d1ra04602k (3D CF+BN/epoxy) =====
M = dict(doi='10.1039/d1ra04602k', source_url='https://doi.org/10.1039/d1ra04602k',
         paper_title='Epoxy composite with high thermal conductivity by constructing 3D-oriented carbon fiber and BN hybrid structure',
         year=2021)
rows_M = []
for cf, k in [('2 mm', 2.4), ('5 mm', 2.7), ('10 mm', 3.1)]:
    r = dict(matrix_polymer='Epoxy resin', curing_agent='',
             filler_material='h-BN', filler_material_original='BN flakes on 3D-oriented carbon fiber (CF) network',
             filler_shape='platelet', functionalization='None',
             filler_alignment='aligned in-plane',
             filler_loading_vol_pct='40', filler_loading_original_value='40',
             filler_loading_original_unit='vol%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W m−1 K−1',
             k_direction='in-plane', measurement_temperature_C='25',
             measurement_method='Laser flash (NETZSCH LFA 457), in-plane and cross-plane at 25 C',
             value_source='text', confidence='High',
             processing_method='Airflow-network + needle-punched 3D CF mat (5 vol% CF), BN coating, vacuum liquid impregnation with epoxy',
             source_location=f'Results text: K= of CF/40 vol% BN/EP up to (values) for {cf} CF',
             notes=f'CF length {cf} (5 vol% CF constant), BN 40 vol%. CF is secondary hybrid component. Cross-plane K values only in Fig 5b (not digitized).')
    rows_M.append(r)
n13, p13 = append_rows(M, rows_M, dict(candidate_id='P013', doi=M['doi'], paper_title=M['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_d1ra04602k.txt',
    tables_inspected='Components table (BN/CF/EP)', figures_inspected='Fig 5 (K in-plane/cross-plane curves; values for 40 vol% BN from text)',
    candidate_measurements=3, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='3 in-plane rows at 25 C; other loadings figure-only'))

# ===== N: 10.3390/polym13010147 (Al2O3/BN hybrid underfill) =====
N = dict(doi='10.3390/polym13010147', source_url='https://doi.org/10.3390/polym13010147',
         paper_title='Enhanced Thermal Conductivity of Epoxy Composites Filled with Al2O3/Boron Nitride Hybrids for Underfill Encapsulation Materials',
         year=2021)
common_N = dict(matrix_polymer='Epoxy (830LVP) with hardener KAYAHARD-AA (1:0.x)',
                curing_agent='KAYAHARD-AA', k_matrix_W_mK='0.22',
                measurement_method='Thermal conductivity via diffusivity (method per text/Fig 6)', k_direction='unknown',
                value_source='text', confidence='High')
rows_N = [
    dict(common_N, filler_material='Al2O3', filler_material_original='micro Al2O3 (m-Al2O3, spherical)',
         filler_shape='Sphere', filler_mean_size_um='5', functionalization='None',
         filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt.%',
         k_composite_W_mK='0.98', k_original_value='0.98', k_original_unit='W·m−1·K−1',
         source_location='Results text Fig 6a discussion: m-Al2O3/EP 60 wt% = 0.98',
         notes='Micro alumina 5 um (Table 1: k=29 W/mK). Optional comparison filler Al2O3.'),
    dict(common_N, filler_material='Al2O3', filler_material_original='nano Al2O3 (n-Al2O3, irregular)',
         filler_shape='irregular', filler_mean_size_um='0.19', functionalization='None',
         filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt.%',
         k_composite_W_mK='0.70', k_original_value='0.70', k_original_unit='W·m−1·K−1',
         source_location='Results text Fig 6a discussion: n-Al2O3/EP 60 wt% = 0.70',
         notes='Nano alumina 0.19 um. Optional comparison filler Al2O3.'),
    dict(common_N, filler_material='Al2O3/BN hybrid', filler_material_original='m-Al2O3-BN hybrid (7:1 m-Al2O3:BN by mass)',
         filler_shape='other', filler_mean_size_um='', functionalization='None',
         filler_loading_wt_pct='80', filler_loading_original_value='80', filler_loading_original_unit='wt.%',
         k_composite_W_mK='1.72', k_original_value='1.72', k_original_unit='W·m−1·K−1',
         source_location='Abstract + text: 80 wt.% hybrid Al2O3-BN -> 1.72 W m-1 K-1',
         notes='Hybrid 7:1 m-Al2O3(sphere 5um):BN(flake 2.5um). BN is secondary component here. Other loadings figure-only.'),
]
n14, p14 = append_rows(N, rows_N, dict(candidate_id='P014', doi=N['doi'], paper_title=N['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13010147.txt',
    tables_inspected='Table 1 (matrix and filler properties)', figures_inspected='Fig 6a referenced',
    candidate_measurements=3, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='3 rows: two alumina-only + one hybrid at 80 wt%'))

# ===== O: 10.3390/nano14020205 (BNNS/G-POSS/epoxy) =====
O = dict(doi='10.3390/nano14020205', source_url='https://doi.org/10.3390/nano14020205',
         paper_title='Significantly Improve the Thermal Conductivity and Dielectric Performance of Epoxy Composite by Constructing BNNSs/G-POSS Double Fillers',
         year=2024)
common_O = dict(matrix_polymer='Epoxy resin', curing_agent='',
                filler_material='BNNS', filler_material_original='BNNSs (boron nitride nanosheets)',
                filler_shape='nanosheet', functionalization='None (BNNS); G-POSS is glycidyl polyhedral oligomeric silsesquioxane secondary filler',
                measurement_method='Plane heat flow method (DRL-III, Xiangtan)', k_direction='unknown',
                value_source='text', confidence='High', k_matrix_W_mK='0.1849')
rows_O = []
for wt, k, extra in [(10, 0.2495, ''), (20, 0.5496, ''), (30, 0.8062, ''), (40, 0.9457, 'max loading tested in Fig 4a')]:
    r = dict(common_O)
    r.update(filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt%', k_composite_W_mK=str(k), k_original_value=str(k),
             k_original_unit='W·m−1·K−1',
             source_location=f'Results text (Fig 4a discussion): BNNSs/epoxy {wt} wt%',
             notes=f'BNNS/epoxy {wt} wt%. Neat epoxy 0.1849 W·m−1·K−1. {extra}')
    rows_O.append(r)
r = dict(common_O)
r.update(filler_loading_wt_pct='22', filler_loading_original_value='20 wt% BNNS + 2 wt% G-POSS',
         filler_loading_original_unit='wt%', k_composite_W_mK='0.3969', k_original_value='0.3969',
         k_original_unit='W·m−1·K−1',
         source_location='Results text (Fig 4b discussion): BNNS/G-POSS/epoxy, G-POSS 2 wt%',
         notes='BNNS 20 wt% + G-POSS 2 wt% total 22 wt% (wt% column=22 total).')
rows_O.append(r)
n15, p15 = append_rows(O, rows_O, dict(candidate_id='P015', doi=O['doi'], paper_title=O['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano14020205.txt',
    tables_inspected='none with k', figures_inspected='Fig 4a/b referenced; values stated in text',
    candidate_measurements=5, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='5 text-sourced rows; hybrid row total loading 22 wt%'))

# ===== P: 10.1039/d1ra00976a (PGMA-grafted BN/epoxy) =====
P = dict(doi='10.1039/d1ra00976a', source_url='https://doi.org/10.1039/d1ra00976a',
         paper_title='Preparation of poly glycidyl methacrylate (PGMA) chain-grafted boron nitride/epoxy composites and study of their thermal conductivity',
         year=2021)
common_P = dict(matrix_polymer='Epoxy resin (EP)', curing_agent='',
                filler_material='BNNS', filler_material_original='h-BN nanosheets (BNNS)',
                filler_shape='nanosheet',
                measurement_method='Hot disk (this-work table row); laser flash for some literature rows',
                k_direction='unknown', value_source='text', confidence='High',
                k_matrix_W_mK='0.23',
                processing_method='h-BN exfoliated; PGMA grafted via ATRP-like grafting from surface (h-BN-PGMA); blended with EP and cured')
rows_P = [
    dict(common_P, functionalization='None',
         filler_loading_vol_pct='4', filler_loading_original_value='4', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.279', k_original_value='0.279', k_original_unit='W m−1 K−1',
         source_location='Results text Fig 9a discussion: EP/h-BN 4 vol% = 0.279',
         notes='Untreated h-BN/epoxy. Neat EP reported as 0.23 W m-1 K-1 in text.'),
    dict(common_P, functionalization='None',
         filler_loading_vol_pct='16', filler_loading_original_value='16', filler_loading_original_unit='vol%',
         k_composite_W_mK='1.052', k_original_value='1.052', k_original_unit='W m−1 K−1',
         source_location='Results text Fig 9a: EP/h-BN 16 vol% = 1.052 (also Table literature-like row 1.052 at 60wt% microBN is ref [3], not this)',
         notes='Untreated h-BN/epoxy 16 vol%. Note Table a row 60wt% micro BN 1.052 is literature [3] - coincidence of value; verify not conflated: text explicitly says EP/h-BN 16 vol% -> 1.052 for this system.'),
    dict(common_P, functionalization='PGMA (poly(glycidyl methacrylate) graft)',
         filler_loading_vol_pct='16', filler_loading_original_value='16', filler_loading_original_unit='vol%',
         k_composite_W_mK='1.197', k_original_value='1.197', k_original_unit='W m−1 K−1',
         source_location='Text: h-BN-PGMA 16 vol% -> 1.197 (Table a this-work row lists 1.198, hot disk)',
         notes='EP/h-BN-PGMA 16 vol%. Table lists 1.198; text states 1.197; retained text value 1.197, both preserved in notes.'),
]
n16, p16 = append_rows(P, rows_P, dict(candidate_id='P016', doi=P['doi'], paper_title=P['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1039_d1ra00976a.txt',
    tables_inspected='Table a (literature + this-work row)', figures_inspected='Fig 9 (k vs vol%)',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='this-work Table row (1.198) merged with text value (1.197) as one measurement; literature rows excluded',
    qc_findings='minor 1.197/1.198 text-table discrepancy documented'))

print(f'BATCH4 appended: M={n13} N={n14} O={n15} P={n16} grand={n13+n14+n15+n16}')
