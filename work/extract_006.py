import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== T: 10.1038/s41598-021-81925-x (alumina + BNNs / epoxy) =====
T = dict(doi='10.1038/s41598-021-81925-x', source_url='https://doi.org/10.1038/s41598-021-81925-x',
         paper_title='Simultaneously enhanced dielectric properties and through-plane thermal conductivity of epoxy composites with alumina and boron nitride nanosheets',
         year=2021)
common_T = dict(matrix_polymer='Epoxy resin', curing_agent='',
                measurement_method='LFA (NETZSCH LFA 467); Cp DSC, rho densimeter',
                k_direction='through-plane', measurement_temperature_C='25 (RT)',
                value_source='text', confidence='High', k_matrix_W_mK='0.18',
                notes_prefix=None)
rows_T = [
    dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='Al2O3', filler_material_original='alumina microspheres (A)',
         filler_shape='Sphere', functionalization='None',
         filler_loading_vol_pct='8', filler_loading_original_value='8', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.32', k_original_value='0.32', k_original_unit='W/m K',
         measurement_method='LFA (NETZSCH LFA 467)', k_direction='through-plane',
         value_source='text', confidence='High', k_matrix_W_mK='0.18',
         source_location='Results text Fig 3a discussion: A8 = 0.32 W/m K',
         notes='A8 = 8 vol% alumina only. Pure epoxy 0.18 W/m K.'),
    dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='Al2O3', filler_material_original='alumina microspheres (A)',
         filler_shape='Sphere', functionalization='None',
         filler_loading_vol_pct='10', filler_loading_original_value='10', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.35', k_original_value='0.35', k_original_unit='W/m K',
         measurement_method='LFA (NETZSCH LFA 467)', k_direction='through-plane',
         value_source='text', confidence='High', k_matrix_W_mK='0.18',
         source_location='Results text Fig 3a discussion: A10 = 0.35 W/m K',
         notes='A10 = 10 vol% alumina only.'),
    dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='Al2O3/BNNS hybrid', filler_material_original='A6+B2 = 6 vol% alumina + 2 vol% BNNs',
         filler_shape='other', functionalization='None',
         filler_loading_vol_pct='8', filler_loading_original_value='8', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.38', k_original_value='0.38', k_original_unit='W/m K',
         measurement_method='LFA (NETZSCH LFA 467)', k_direction='through-plane',
         value_source='text', confidence='High', k_matrix_W_mK='0.18',
         source_location='Results text: A6+B2 through-plane = 0.38 W/m K',
         notes='Total 8 vol% (6 vol% Al2O3 + 2 vol% BNNs). Hybrid synergy row.'),
    dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='Al2O3/BNNS hybrid', filler_material_original='A6+B4 = 6 vol% alumina + 4 vol% BNNs',
         filler_shape='other', functionalization='None',
         filler_loading_vol_pct='10', filler_loading_original_value='10', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.47', k_original_value='0.47', k_original_unit='W/m K',
         measurement_method='LFA (NETZSCH LFA 467)', k_direction='through-plane',
         value_source='text', confidence='High', k_matrix_W_mK='0.18',
         source_location='Results text: A6+B4 through-plane = 0.47 W/m K',
         notes='Total 10 vol% (6 vol% Al2O3 + 4 vol% BNNs). Hybrid synergy row.'),
]
n1, p1 = append_rows(T, rows_T, dict(candidate_id='P020', doi=T['doi'], paper_title=T['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1038_s41598-021-81925-x.txt',
    tables_inspected='none with k', figures_inspected='Fig 3a curves (values quoted in text)',
    candidate_measurements=4, unit_conversions='none (vol% native)', duplicate_checks='none needed',
    qc_findings='4 rows: 2 alumina-only + 2 hybrid; A2/A4/A6 only in figure'))

# ===== U: 10.1007/s42114-023-00804-3 (BNWK@Al2O3 / cellulose aerogel / epoxy) =====
U = dict(doi='10.1007/s42114-023-00804-3', source_url='https://doi.org/10.1007/s42114-023-00804-3',
         paper_title='Vertically aligned BNWK@Al2O3 network in cellulose aerogel for thermally conductive epoxy composites',
         year=2023)
common_U = dict(matrix_polymer='Epoxy resin (EP), cellulose aerogel (CA) scaffold',
                curing_agent='',
                filler_material='BN', filler_material_original='BNWK@Al2O3 (BN whisker @ nano-Al2O3 core-shell, 1:7) in cellulose aerogel',
                filler_shape='whisker/nanowire', functionalization='nano-Al2O3 coating on BNWK',
                filler_alignment='vertically aligned',
                filler_loading_wt_pct='8.6', filler_loading_original_value='8.6', filler_loading_original_unit='wt%',
                measurement_method='Thermal conductivity of composites (method per text; vertical direction)', k_direction='through-plane (vertical)',
                value_source='text', confidence='High', k_matrix_W_mK='0.2')
rows_U = [
    dict(common_U, k_composite_W_mK='1.92', k_original_value='1.92', k_original_unit='W/(m·K)',
         processing_method='Directional freeze-drying of CA scaffold, vacuum EP impregnation',
         source_location='Abstract/conclusion: BNWK@Al2O3(1:7)/CA/EP 8.6 wt% -> 1.92',
         notes='Optimal 1:7 BNWK:nano-Al2O3, total 8.6 wt%.'),
    dict(common_U, k_composite_W_mK='1.04', k_original_value='1.04', k_original_unit='W/(m·K)',
         processing_method='Directional freeze-drying, vacuum EP impregnation',
         source_location='Results Fig 5a text: ratio 1:1 -> 1.04 W/(m·K)',
         notes='BNWK@Al2O3 1:1, total 8.6 wt% (total loading assumed same series - confirm: text says ratios change from 1:1 to 1:7 with k 1.04 to 1.92).'),
    dict(common_U, k_composite_W_mK='0.87', k_original_value='0.87', k_original_unit='W/(m·K)',
         processing_method='Simple blending (comparison sample), same 1:7 filler',
         source_location='Conclusion text: BNWK@Al2O3(1:7)/CA/EP (Blend) = 0.87 W/(m·K)',
         notes='Same filler loading 8.6 wt%, ordinary blending instead of aligned network - processing comparison row.'),
]
n2, p2 = append_rows(U, rows_U, dict(candidate_id='P021', doi=U['doi'], paper_title=U['paper_title'],
    date_processed='2026-10-13', access_result='PDF-to-text (Springer OA)',
    files_inspected='work/fulltext/10.1007_s42114-023-00804-3.txt',
    tables_inspected='none with k', figures_inspected='Fig 5a (values quoted in text)',
    candidate_measurements=3, unit_conversions='none', duplicate_checks='BNWK-only 0.48 excluded: filler loading not stated in text',
    qc_findings='3 rows; BNWK/CA/EP 0.48 not extracted (missing loading); ratio-series 1:0.5..1:3 intermediate figure-only'))

# ===== V: 10.1039/d3ra00428g (hydroxy-silicone-oil-modified BN / silicone rubber) =====
V = dict(doi='10.1039/d3ra00428g', source_url='https://doi.org/10.1039/d3ra00428g',
         paper_title='Hydroxy silicone oil modified boron nitride for high thermal conductivity and low dielectric loss silicone rubber composites',
         year=2023)
r = dict(matrix_polymer='Silicone rubber (SiR)', curing_agent='',
         filler_material='BN', filler_material_original='Si11 = long-chain hydroxyl silicone oil modified BN',
         filler_shape='platelet', functionalization='Hydroxyl silicone oil graft (chain length 11)',
         filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.88', k_original_value='1.88', k_original_unit='W m−1 K−1',
         measurement_method='TPS1500 hot disk (isotropic, sample thickness ~6 mm)', k_direction='isotropic',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='Silicone rubber compounding with modified BN, curing',
         source_location='Results text: TC reaches 1.88 W m-1 K-1 at 40 wt% Si11 in silicone rubber',
         notes='Optional matrix: silicone rubber (not epoxy). Pure SiR k not numerically stated (only +683.3%). Intermediate loadings figure-only (Fig 6a).')
n3, p3 = append_rows(V, [r], dict(candidate_id='P022', doi=V['doi'], paper_title=V['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML (RSC)',
    files_inspected='work/fulltext/10.1039_d3ra00428g.txt',
    tables_inspected='none with k', figures_inspected='Fig 6a (k vs loading)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='Fig 6b literature dataset excluded',
    qc_findings='1 row, optional silicone-rubber matrix'))

# ===== W: 10.3390/polym12091954 (a-BN + SAC305 3D network / epoxy) =====
W = dict(doi='10.3390/polym12091954', source_url='https://doi.org/10.3390/polym12091954',
         paper_title='3D Filler Network of Angular BN and SAC305 Solder in Epoxy for Enhanced Thermal Conductivity',
         year=2015)
common_W = dict(matrix_polymer='Epoxy resin', curing_agent='',
                measurement_method='LFA (Netzsch Nanoflash LFA 447); thermal diffusivity, Cp, rho',
                k_direction='unknown', value_source='text', confidence='High', k_matrix_W_mK='0.19')
rows_W = [
    dict(common_W, filler_material='h-BN', filler_material_original='a-BN + SAC305 (Sn63Pb37) hybrid 1:0.5, 1 g a-BN on 3 g epoxy',
         filler_shape='platelet', functionalization='None (hybrid with SAC305 solder)',
         filler_alignment='3D network (hot-pressed)',
         filler_loading_wt_pct='33', filler_loading_original_value='33', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.95', k_original_value='0.95', k_original_unit='W/mK',
         processing_method='SAC305+a-BN hot-pressed 3D network infiltrated with epoxy',
         source_location='Abstract + Results: hybrid filler (a-BN:SAC305 = 1:0.5) reached 0.95 W/mK (33 wt%)',
         notes='Total filler 33 wt% (1 g a-BN + 0.5 g SAC305 per 3 g epoxy). SAC305 is metallic secondary component.'),
    dict(common_W, filler_material='h-BN', filler_material_original='raw a-BN (angular BN)',
         filler_shape='platelet', functionalization='None',
         filler_loading_wt_pct='25', filler_loading_original_value='25', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.60', k_original_value='0.60', k_original_unit='W/mK',
         source_location='Abstract: raw a-BN only 0.60 W/mK (25 wt%)',
         notes='Raw a-BN 1 g / 3 g epoxy = 25 wt%. CONFLICT: Results text also states 0.82 W/mK for raw a-BN "with equivalent amount of a-BN" - two reported values for near-identical loading; 0.60 (abstract) retained, 0.82 documented here. Confidence downgraded.'),
]
n4, p4 = append_rows(W, rows_W, dict(candidate_id='P023', doi=W['doi'], paper_title=W['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym12091954.txt',
    tables_inspected='none with k', figures_inspected='k vs hybrid ratio curves',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='0.60/0.82 raw-BN conflict documented not duplicated',
    qc_findings='2 rows; 1:1,1:2,2:1,3:1 hybrid ratios figure-only; abstract/text 0.60 vs 0.82 discrepancy flagged'))

print(f'BATCH6 appended: T={n1} U={n2} V={n3} W={n4} grand={n1+n2+n3+n4}')
