import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== FIX: re-append O hybrid row rejected for non-numeric original loading =====
OFIX = dict(doi='10.3390/nano14020205', source_url='https://doi.org/10.3390/nano14020205',
            paper_title='Significantly Improve the Thermal Conductivity and Dielectric Performance of Epoxy Composite by Constructing BNNSs/G-POSS Double Fillers',
            year=2024)
r = dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='BNNS', filler_material_original='BNNSs + G-POSS (glycidyl POSS double filler)',
         filler_shape='nanosheet', functionalization='G-POSS secondary filler',
         filler_loading_wt_pct='22', filler_loading_original_value='22',
         filler_loading_original_unit='wt%',
         k_composite_W_mK='0.3969', k_original_value='0.3969', k_original_unit='W·m−1·K−1',
         measurement_method='Plane heat flow method (DRL-III, Xiangtan)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.1849',
         source_location='Results text (Fig 4b discussion): BNNS/G-POSS/epoxy',
         notes='20 wt% BNNS + 2 wt% G-POSS (total 22 wt%, kept numeric in loading fields).')
n1, p1 = append_rows(OFIX, [r], dict(candidate_id='P015', doi=OFIX['doi'], paper_title=OFIX['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano14020205.txt',
    tables_inspected='none with k', figures_inspected='Fig 4b',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='retry of rejected ad883006-073',
    qc_findings='non-numeric original loading rejected; re-appended numeric 22 wt% with composition in notes'))

# ===== Q: 10.3390/gels12070644 (PDA-modified BN in silicone gel) =====
Q = dict(doi='10.3390/gels12070644', source_url='https://doi.org/10.3390/gels12070644',
         paper_title='Polydopamine-Modified Boron Nitride Silicone Gel Composites with Enhanced Thermal Conductivity and Insulation',
         year=2025)
common_Q = dict(matrix_polymer='Silicone gel (SG)', curing_agent='',
                filler_material='BNNS', filler_material_original='P-BN (polydopamine-modified h-BN nanosheets)',
                filler_shape='nanosheet', functionalization='Polydopamine (PDA)',
                measurement_method='Hot Disk TPS 2500S (thermal constants analyzer), room temperature',
                k_direction='unknown', value_source='text', confidence='High',
                k_matrix_W_mK='0.183',
                source_location='Results text k section: SG/P-BN_k values at RT')
rows_Q = []
for idx, wt, k in [(1, 1, 0.224), (2, 2, 0.237), (3, 3, 0.250), (4, 4, 0.246)]:
    r = dict(common_Q)
    r.update(filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
             filler_loading_original_unit='wt%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W/m·K',
             notes=f'SG/P-BN{idx} = {wt} wt% P-BN. Optional matrix: silicone gel (encapsulation gel), not epoxy.')
    if idx == 3:
        r['notes'] += ' Highest k among series.'
    if idx == 4:
        r['notes'] += ' Slight drop vs P-BN3 (agglomeration per authors).'
    rows_Q.append(r)
n2, p2 = append_rows(Q, rows_Q, dict(candidate_id='P017', doi=Q['doi'], paper_title=Q['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_gels12070644.txt',
    tables_inspected='none with k (values in text)', figures_inspected='k curves referenced',
    candidate_measurements=4, unit_conversions='none', duplicate_checks='neat SG 0.183 kept as k_matrix not row',
    qc_findings='4 rows, optional silicone-gel matrix, method Hot Disk RT'))

# ===== R: 10.3390/polym13050694 (AgNW-AlN 3D network / epoxy) =====
R = dict(doi='10.3390/polym13050694', source_url='https://doi.org/10.3390/polym13050694',
         paper_title='Epoxy Composites with 3D AgNW-AlN Network for Thermally Conductive yet Electrical Insulating Interface Materials',
         year=2021)
r = dict(matrix_polymer='Epoxy resin (EP)', curing_agent='',
         filler_material='AlN', filler_material_original='AgNW-sintered AlN (AA) 3D network',
         filler_shape='other', functionalization='AgNW coating on AlN (sintered scaffold)',
         filler_alignment='3D network (percolating)',
         filler_loading_vol_pct='49.86', filler_loading_original_value='49.86',
         filler_loading_original_unit='vol.%',
         k_composite_W_mK='4.49', k_original_value='4.49', k_original_unit='W m−1 K−1',
         k_direction='through-plane (perpendicular)', measurement_temperature_C='25',
         measurement_method='LFA (Netzsch NanoFlash LFA 467), through-plane; Cp DSC, rho densimeter',
         value_source='text', confidence='High', k_matrix_W_mK='0.22',
         processing_method='Polyol-synthesized AgNW-AlN hybrid, hot-pressed sintered 3D network, vacuum epoxy impregnation',
         source_location='Abstract + Results: 400-1:1 sample, 49.86 vol% -> 4.49 W m-1 K-1',
         notes='Sample 400 mg, AlN:AgNW 1:1. Other network ratios/loadings in figures only. Neat EP 0.22.')
n3, p3 = append_rows(R, [r], dict(candidate_id='P018', doi=R['doi'], paper_title=R['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13050694.txt',
    tables_inspected='none with k', figures_inspected='k ratios 1:1/1:2/2:1/3:1 curves (figure-only)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='lit values (4.45 AlN honeycomb, 6.11 BN foam) excluded as literature',
    qc_findings='1 text row; AgNW is conductive scaffold - AlN primary filler recorded'))

# ===== S: 10.3390/polym13193253 (BNNS structural film adhesive) =====
S = dict(doi='10.3390/polym13193253', source_url='https://doi.org/10.3390/polym13193253',
         paper_title='Thermally Conductive Epoxy Structural Film Adhesive with BN Nanosheets and Polyester Fabric Carrier',
         year=2021)
r = dict(matrix_polymer='Epoxy (PHO-modified) / DDS hardener, polyester fabric carrier',
         curing_agent='DDS',
         filler_material='BNNS', filler_material_original='BN nanosheets (nano-BN)',
         filler_shape='nanosheet', functionalization='None',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt.%',
         k_composite_W_mK='0.65', k_original_value='0.65', k_original_unit='W/mK',
         measurement_method='LFA (Netzsch LFA 457 Microflash)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.21',
         processing_method='Double-roll milling; film cast at 70 C via three-roll mill; Ep/PHO30/nBN30 formulation',
         source_location='Abstract + text: Ep/PHO30/nBN30 -> 0.65 W/mK (Tg 215 C)',
         notes='30 wt% BNNS in PHO30 epoxy; unmodified adhesive (0 BN) = 0.21 W/mK. Intermediate loadings in Fig S3/Table S1 (SI, not accessible).')
n4, p4 = append_rows(S, [r], dict(candidate_id='P019', doi=S['doi'], paper_title=S['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13193253.txt',
    tables_inspected='Table S1 in SI (not retrieved)', figures_inspected='Fig S3 referenced (SI)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='only max-loading row text-accessible; SI contains full series'))

print(f'BATCH5 appended: fix={n1} Q={n2} R={n3} S={n4} grand={n1+n2+n3+n4}')
