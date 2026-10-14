import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== H: 10.3390/polym12092072 (silicone + hBN / FL-hBN) =====
H = dict(doi='10.3390/polym12092072', source_url='https://doi.org/10.3390/polym12092072',
         paper_title='Enhanced Thermal Conductivity of Silicone Composites Filled with Few-Layered Hexagonal Boron Nitride Synthesized by Fluid-Promoted Exfoliation',
         year=2020)
common_H = dict(matrix_polymer='Silicone rubber', curing_agent='',
                measurement_method='Laser flash (NETZSCH LFA 457 MicroFlash); k = density x Cp x diffusivity',
                k_direction='unknown', value_source='table', confidence='High',
                processing_method='Fluid-promoted exfoliation of h-BN (CMC/TW80/SDS media) then solution mixing into silicone',
                k_matrix_W_mK='0.244')
rows_H = []
for fill, orig, sh, wt, k in [
    ('h-BN', 'h-BN', 'platelet', 10, 0.344), ('h-BN', 'h-BN', 'platelet', 20, 0.357),
    ('h-BN', 'h-BN', 'platelet', 30, 0.424),
    ('BNNS', 'FL-hBN (few-layered h-BN)', 'nanosheet', 10, 0.418),
    ('BNNS', 'FL-hBN (few-layered h-BN)', 'nanosheet', 20, 0.438),
    ('BNNS', 'FL-hBN (few-layered h-BN)', 'nanosheet', 30, 0.515)]:
    r = dict(common_H)
    r.update(filler_material=fill, filler_material_original=orig, filler_shape=sh,
             functionalization='None',
             filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt.%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W m−1 K−1',
             source_location=f'Table 1 row {orig} {wt} wt.%',
             notes='Optional matrix (silicone). Density/Cp/diffusivity also in Table 1. Pure silicone k=0.244 W/mK.')
    rows_H.append(r)
n8, p8 = append_rows(H, rows_H, dict(candidate_id='P008', doi=H['doi'], paper_title=H['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym12092072.txt',
    tables_inspected='Table 1 (physical properties incl. thermal conductivity)', figures_inspected='',
    candidate_measurements=6, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='optional matrix silicone; 6 rows'))

# ===== I: 10.1021/acsanm.4c01646 (BNNS/BNNT hybrid, two epoxies) =====
I = dict(doi='10.1021/acsanm.4c01646', source_url='https://doi.org/10.1021/acsanm.4c01646',
         paper_title='Synergistic Improvement in the Thermal Conductivity of Hybrid Boron Nitride Nanotube/Nanosheet/Epoxy Composites by Constructing a Dual-Scale Filler Network',
         year=2024)
rows_I = []
for mat, cure, kn, note in [
    ('Araldite LY564 epoxy (DGEBA)', 'Aradur 2954 (100:38)', '3.43',
     'Table 1 lists 3.43 and 2.6 for LY654 and LY5052 in that order; text says 2.6 and 3.4 for fig3b context - mapping taken from Table 1 order'),
    ('Araldite LY5052 epoxy (epoxy phenol novolac)', 'Aradur HY5052', '2.6',
     'mapping from Table 1 order (LY564 and LY5052 -> 3.43 and 2.6); slight ambiguity vs text sentence order')]:
    r = dict(matrix_polymer=mat, curing_agent=cure,
             filler_material='BNNS', filler_material_original='BNNS + BNNT (multiwalled boron nitride nanotubes)',
             filler_shape='nanosheet', functionalization='None',
             filler_loading_wt_pct='31', filler_loading_original_value='30 wt% BNNS + 1 wt% BNNT',
             filler_loading_original_unit='wt%',
             k_composite_W_mK=kn, k_original_value=kn, k_original_unit='Wm–1 K–1',
             k_direction='through-plane', measurement_method='Laser flash (NETZSCH LFA 427), through-plane',
             k_matrix_W_mK=('0.27' if 'LY564' in mat else '0.2'),
             value_source='table', confidence='Medium',
             source_location='Table 1 this-work row; text (neat k values; hybrid sentence)',
             notes=note + '. Loading column 31 = 30 BNNS + 1 BNNT wt%. ChemRxiv preprint also exists (10.26434/chemrxiv-2024-n9mn8).')
    rows_I.append(r)
n9, p9 = append_rows(I, rows_I, dict(candidate_id='P009', doi=I['doi'], paper_title=I['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1021_acsanm.4c01646.txt',
    tables_inspected='Table 1 (k values of epoxy composites; this-work rows only)',
    figures_inspected='Figure 3 (k vs filler contents) referenced; not digitized',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='preprint 10.26434/chemrxiv-2024-n9mn8 same study - not counted separately',
    qc_findings='medium confidence: dual-epoxy value mapping ambiguity between Table 1 order and text sentence order'))

# ===== J: 10.3390/nano13010138 (plasma-treated BNNS/epoxy) =====
J = dict(doi='10.3390/nano13010138', source_url='https://doi.org/10.3390/nano13010138',
         paper_title='Effect of Ambient Plasma Treatments on Thermal Conductivity and Fracture Toughness of Boron Nitride Nanosheets/Epoxy Composites',
         year=2022)
common_J = dict(matrix_polymer='DGEBA epoxy (YD-128)', curing_agent='DDM (4,4-diaminodiphenylmethane)',
                filler_material='BNNS', filler_material_original='BNNS (from h-BN exfoliation)',
                filler_shape='nanosheet', filler_loading_wt_pct='30',
                filler_loading_original_value='30', filler_loading_original_unit='wt.%',
                measurement_method='Laser flash (NETZSCH LFA-447)', k_direction='unknown',
                value_source='table', confidence='High',
                processing_method='Ambient plasma treatment of BNNS (0/5/7 min) then dispersion in DGEBA/DDM')
rows_J = []
for samp, func, k, note in [
    ('neat BNNS composite (no plasma)', 'None', 0.372, 'untreated BNNS/epoxy reference'),
    ('PBE-5', 'Ambient plasma 5 min', 0.446, ''),
    ('PBE-7', 'Ambient plasma 7 min', 0.535, 'optimal treatment time')]:
    r = dict(common_J)
    r.update(functionalization=func, k_composite_W_mK=str(k), k_original_value=str(k),
             k_original_unit='W∙m−1∙K−1',
             source_location=f'Table 1 / text section Thermal Conductivity of PBE, sample {samp}',
             notes=f'Sample {samp}. {note}. All 30 wt% BNNS. PBE-5 and PBE-7 values confirmed in text (0.446, 0.535); neat-BNNS composite 0.372 in text.')
    rows_J.append(r)
n10, p10 = append_rows(J, rows_J, dict(candidate_id='P010', doi=J['doi'], paper_title=J['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano13010138.txt',
    tables_inspected='Table 1 (this-work row PBE-7)', figures_inspected='Figure 6a (k vs plasma time; partial values in text)',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='literature rows of Table 1 excluded',
    qc_findings='3 rows: untreated + 2 plasma times; other plasma times figure-only'))

# ===== K: 10.3390/polym11081359 (epoxy-impregnated paper + nano-h-BN) =====
K = dict(doi='10.3390/polym11081359', source_url='https://doi.org/10.3390/polym11081359',
         paper_title='Dielectric and Thermal Conductivity of Epoxy Resin Impregnated Nano-h-BN Modified Insulating Paper',
         year=2019)
rows_K = [dict(matrix_polymer='Epoxy resin impregnated insulating paper (RIP)',
               curing_agent='',
               filler_material='h-BN', filler_material_original='nano-h-BN',
               filler_shape='unknown', functionalization='None',
               k_matrix_W_mK='0.203',
               k_composite_W_mK='0.478', k_original_value='0.478', k_original_unit='W/(m·K)',
               filler_loading_wt_pct='50', filler_loading_original_value='50', filler_loading_original_unit='wt %',
               k_direction='unknown', measurement_method='Thermal conductivity tester DTC-300 (TA Instruments)',
               value_source='text', confidence='High',
               source_location='Results text: unmodified RIP k=0.203; 50 wt% nano-h-BN max k=0.478',
               notes='Matrix is epoxy-impregnated paper (epoxy-based insulation system). Intermediate loadings (2.5-40 wt%) only in Figure (not digitized).')]
n11, p11 = append_rows(K, rows_K, dict(candidate_id='P011', doi=K['doi'], paper_title=K['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11081359.txt',
    tables_inspected='Tables 1-2 (CTE params only)', figures_inspected='k vs content figure referenced (not digitized)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='1 row from text; matrix is impregnated paper (flagged)'))

# ===== L: 10.3390/polym15061415 (KH550-modified BN/epoxy) =====
L = dict(doi='10.3390/polym15061415', source_url='https://doi.org/10.3390/polym15061415',
         paper_title='Synthesis of KH550-Modified Hexagonal Boron Nitride Nanofillers for Improving Thermal Conductivity of Epoxy Nanocomposites',
         year=2023)
common_L = dict(matrix_polymer='Epoxy resin', curing_agent='',
                filler_material='h-BN', filler_shape='nanosheet',
                measurement_method='Quick thermal conductivity meter (Xiangyi)', k_direction='unknown',
                k_matrix_W_mK='0.208', value_source='text', confidence='High',
                processing_method='Ball-milling of h-BN (optionally with KH550 silane) to exfoliate, then blend with epoxy and cure')
rows_L = []
for samp, orig, func, wt, k in [
    ('BM@KH550/epoxy', 'BM@KH550-BN (ball-milled KH550-modified BN)', 'Silane KH550 (gamma-aminopropyl triethoxysilane)', 4, 0.328),
    ('R-BN/epoxy', 'R-BN (raw BN)', 'None', 7, 0.307),
    ('BM-BN/epoxy', 'BM-BN (ball-milled BN)', 'None', 7, 0.354),
    ('BM-KH550/epoxy', 'BM-KH550-BN (ball-milled + KH550)', 'Silane KH550', 7, 0.391),
    ('BM@KH550/epoxy', 'BM@KH550-BN (ball-milled KH550-modified BN)', 'Silane KH550', 7, 0.431),
    ('R-BN/epoxy', 'R-BN (raw BN)', 'None', 10, 0.325),
    ('BM-BN/epoxy', 'BM-BN (ball-milled BN)', 'None', 10, 0.433),
    ('BM-KH550/epoxy', 'BM-KH550-BN (ball-milled + KH550)', 'Silane KH550', 10, 0.507),
    ('BM@KH550/epoxy', 'BM@KH550-BN (ball-milled KH550-modified BN)', 'Silane KH550', 10, 0.615)]:
    r = dict(common_L)
    r.update(filler_material_original=orig, functionalization=func,
             filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W m−1 K−1',
             source_location=f'Results text Thermal Conductivity Analysis section, sample {samp} at {wt} wt%',
             notes=f'Sample {samp}. Neat epoxy 0.208 W m−1 K−1. Ball-milled fillers rich in BN nanosheets.')
    rows_L.append(r)
n12, p12 = append_rows(L, rows_L, dict(candidate_id='P012', doi=L['doi'], paper_title=L['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym15061415.txt',
    tables_inspected='Table 1 (DMA only)', figures_inspected='Figure 6A/B referenced; values stated in text',
    candidate_measurements=9, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='9 text-sourced rows across 4 filler types x loadings'))

print(f'BATCH3 appended: H={n8} I={n9} J={n10} K={n11} L={n12} grand={n8+n9+n10+n11+n12}')
