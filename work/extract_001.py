import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ============ PAPER A: 10.3390/polym10030340 ============
A = dict(doi='10.3390/polym10030340',
         source_url='https://doi.org/10.3390/polym10030340',
         paper_title='Epoxy-Thiol Systems Filled with Boron Nitride for High Thermal Conductivity Applications',
         year=2018)
common_A = dict(matrix_polymer='Epoxy-thiol (DGEBA epoxy + thiol network)',
                curing_agent='Thiol hardener (LC-80), imidazole initiator',
                filler_material='h-BN', filler_material_original='boron nitride (BN)',
                functionalization='None', k_matrix_W_mK='0.20',
                measurement_method='Transient hot bridge (Linseis THB-100)',
                k_direction='unknown',
                value_source='table', confidence='High')
rows_A = []
for s, wt, vol, k, shape, size, note in [
    ('ETLBN80-30', 20.3, 13.4, 0.80, 'other', '80', 'spherical agglomerates of platelets (80 um BN)'),
    ('ETLBN80-50', 37.2, 26.7, 2.21, 'other', '80', 'spherical agglomerates of platelets (80 um BN)'),
    ('ETLBN80-60', 47.1, 35.0, 3.40, 'other', '80', 'spherical agglomerates of platelets (80 um BN)'),
    ('ETLBN80/2-30', 25.3, 17.1, 0.77, 'platelet', '', 'hybrid: 80 um agglomerates + 2 um platelets; vol% is measured value; size not single-valued'),
    ('ETLBN80/2-50', 44.2, 32.4, 2.72, 'platelet', '', 'hybrid: 80 um agglomerates + 2 um platelets; vol% measured; size not single-valued'),
    ('ETLBN80/2-60', 54.2, 40.8, 4.02, 'platelet', '', 'hybrid: 80 um agglomerates + 2 um platelets; vol% measured; size not single-valued'),
    ('ETLBN80/6-30', 25.3, 17.1, 0.75, 'platelet', '', 'hybrid: 80 um agglomerates + 6 um platelets; vol% measured; size not single-valued'),
    ('ETLBN80/6-50', 44.2, 33.0, 2.71, 'platelet', '', 'hybrid: 80 um agglomerates + 6 um platelets; vol% measured; size not single-valued'),
    ('ETLBN80/6-60', 54.2, 42.1, 4.17, 'platelet', '', 'hybrid: 80 um agglomerates + 6 um platelets; vol% measured; size not single-valued'),
]:
    r = dict(common_A)
    r.update(matrix_polymer='Epoxy-thiol (DGEBA epoxy + thiol network)',
             filler_shape=shape, filler_mean_size_um=size,
             filler_loading_wt_pct=str(wt), filler_loading_vol_pct=str(vol),
             filler_loading_original_value=str(vol), filler_loading_original_unit='vol%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W/mK',
             source_location=f'Table 4 (k, measured vol%); Table 1 (wt%) sample {s}',
             notes=f'Sample {s}. Neat ETL k=0.20 W/mK from Table 4. {note}. vol% measured by density (Archimedes).')
    rows_A.append(r)
n1, p1 = append_rows(A, rows_A, dict(candidate_id='P001', doi=A['doi'], paper_title=A['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym10030340.txt',
    tables_inspected='Table 1 (compositions), Table 4 (densities and thermal conductivities)',
    figures_inspected='', candidate_measurements=9, unit_conversions='none (W/mK direct)',
    duplicate_checks='none needed', qc_findings='all 9 rows high confidence, table-sourced'))

# ============ PAPER B: 10.3390/polym13060955 ============
B = dict(doi='10.3390/polym13060955',
         source_url='https://doi.org/10.3390/polym13060955',
         paper_title='Remarkable Thermal Conductivity of Epoxy Composites Filled with Boron Nitride and Cured under Pressure',
         year=2021)
common_B = dict(filler_material='h-BN', filler_material_original='hexagonal BN (Saint Gobain)',
                functionalization='None',
                measurement_method='Transient hot bridge (Linseis THB-100)',
                k_direction='unknown', value_source='table', confidence='High')
rows_B = []
def addB(sample, matrix, cure, size, shape, wt, vol, k, cond, extra=''):
    r = dict(common_B)
    r.update(matrix_polymer=matrix, curing_agent=cure, filler_shape=shape,
             filler_mean_size_um=size,
             filler_loading_wt_pct=str(wt), filler_loading_vol_pct=str(vol),
             filler_loading_original_value=str(vol), filler_loading_original_unit='vol%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W/mK',
             processing_method=cond,
             source_location=f'Table 2 sample {sample}',
             notes=f'Sample {sample} ({cond}). wt% from Table 1. {extra}'.strip())
    rows_B.append(r)

ETL = 'Epoxy-thiol (DGEBA + thiol)'
EJ = 'Epoxy-diamine (DGEBA + Jeffamine D-230)'
CT = 'Thiol hardener (LC-80)'
CA = 'Jeffamine D-230'
addB('ETLBN2-60', ETL, CT, '2', 'platelet', 60, 34.2, 1.28, 'Cured at ambient pressure')
addB('ETLBN2-60', ETL, CT, '2', 'platelet', 60, 34.2, 1.49, 'Cured under 175 kPa')
addB('ETLBN30-60', ETL, CT, '30', 'platelet', 60, 34.2, 2.36, 'Cured at ambient pressure')
addB('ETLBN30-60', ETL, CT, '30', 'platelet', 60, 34.2, 4.44, 'Cured under 175 kPa')
addB('ETLBN30-70', ETL, CT, '30', 'platelet', 70, 44.7, 3.34, 'Cured at ambient pressure')
addB('ETLBN30-70', ETL, CT, '30', 'platelet', 70, 44.7, 4.77, 'Cured under 175 kPa')
addB('ETLBN30-70', ETL, CT, '30', 'platelet', 70, 44.7, 7.67, 'Cured under 2 MPa')
addB('ETLBN180-60', ETL, CT, '180', 'platelet', 60, 34.2, 3.02, 'Cured at ambient pressure')
addB('ETLBN180-60', ETL, CT, '180', 'platelet', 60, 34.2, 3.80, 'Cured under 175 kPa')
addB('ETLBN180-70', ETL, CT, '180', 'platelet', 70, 44.7, 4.22, 'Cured at ambient pressure')
addB('ETLBN180-70', ETL, CT, '180', 'platelet', 70, 44.7, 5.38, 'Cured under 175 kPa')
addB('ETLBN180-70', ETL, CT, '180', 'platelet', 70, 44.7, 8.52, 'Cured under 2 MPa')
addB('ETLBN120s-60', ETL, CT, '120', 'other', 60, 34.2, 3.42, 'Cured at ambient pressure',
     '120 um = agglomerates of platelets (sample label suffix s)')
addB('ETLBN120s-60', ETL, CT, '120', 'other', 60, 34.2, 5.34, 'Cured under 175 kPa',
     '120 um = agglomerates of platelets')
addB('ETLBN120s-70', ETL, CT, '120', 'other', 70, 44.7, 5.55, 'Cured under 175 kPa',
     'no ambient-pressure value reported; 120 um agglomerates')
addB('ETLBN120s-70', ETL, CT, '120', 'other', 70, 44.7, 10.49, 'Cured under 2 MPa',
     '120 um agglomerates')
addB('EJBN30-60', EJ, CA, '30', 'platelet', 60, 38.1, 1.87, 'Cured at ambient pressure')
addB('EJBN30-60', EJ, CA, '30', 'platelet', 60, 38.1, 4.19, 'Cured under 175 kPa')
addB('EJBN30-65', EJ, CA, '30', 'platelet', 65, 43.3, 2.37, 'Cured at ambient pressure')
addB('EJBN30-65', EJ, CA, '30', 'platelet', 65, 43.3, 4.32, 'Cured under 175 kPa')
n2, p2 = append_rows(B, rows_B, dict(candidate_id='P002', doi=B['doi'], paper_title=B['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13060955.txt',
    tables_inspected='Table 1 (compositions), Table 2 (densities and thermal conductivities vs cure pressure)',
    figures_inspected='', candidate_measurements=19, unit_conversions='none',
    duplicate_checks='distinct cure-pressure conditions kept as separate rows per Section 6.4',
    qc_findings='20 rows appended; vol% repeated across size grades as reported in Table 1'))

# ============ PAPER C: 10.3390/nano8040242 ============
C = dict(doi='10.3390/nano8040242',
         source_url='https://doi.org/10.3390/nano8040242',
         paper_title='Alignment of Boron Nitride Nanofibers in Epoxy Composite Films for Thermal Conductivity and Dielectric Performance',
         year=2018)
common_C = dict(matrix_polymer='Epoxy E-828 (DGEBA)',
                curing_agent='MTHPA anhydride with BDMA accelerant (ratio 1/0.85/0.01 approx as reported)',
                filler_material='h-BN', filler_material_original='boron nitride nanofibers (BNNF)',
                filler_shape='fiber',
                functionalization='None', k_matrix_W_mK='0.162',
                measurement_method='Laser flash (NETZSCH LFA 467 Nanoflash)',
                k_direction='unknown', value_source='table', confidence='High',
                processing_method='Electrospun BNNF coated with epoxy, film casting; nanofibers preferentially oriented in-plane')
rows_C = []
for wt, k in [('0.5', 0.17), ('1', 0.185), ('2', 0.205)]:
    r = dict(common_C)
    r.update(filler_loading_wt_pct=wt, filler_loading_original_value=wt, filler_loading_original_unit='wt%',
             k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W/mK',
             source_location=f'Table 1 row {wt} wt%',
             notes='vol% not reported. Neat epoxy lambda=0.162 W/mK (Table 1). LFA on freestanding films; measurement direction not explicitly stated in text/table.')
    rows_C.append(r)
n3, p3 = append_rows(C, rows_C, dict(candidate_id='P003', doi=C['doi'], paper_title=C['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano8040242.txt',
    tables_inspected='Table 1 (thermal diffusivity, lambda, DBS vs mass fraction)',
    figures_inspected='', candidate_measurements=3, unit_conversions='none',
    duplicate_checks='none needed', qc_findings='direction unreported; retained with k_direction=unknown'))

# ============ PAPER D: 10.3390/polym12020426 ============
D = dict(doi='10.3390/polym12020426',
         source_url='https://doi.org/10.3390/polym12020426',
         paper_title='Synergistic Effects of Boron Nitride (BN) Nanosheets and Silver (Ag) Nanoparticles on Thermal Conductivity of Epoxy Composites',
         year=2020)
common_D = dict(matrix_polymer='Epoxy E-51 (DGEBA)',
                curing_agent='593 curing agent (adduct of diethylenetriamine and butyl glycidyl ether), epoxy/curing agent 4:1',
                functionalization='None (BNNS); AgNPs deposited on BNNS for hybrid filler',
                measurement_method='Steady-state heat flow, DRL-III (ASTM D5470-2006)',
                k_direction='unknown', value_source='table', confidence='High',
                k_matrix_W_mK='0.18',
                processing_method='Liquid-phase exfoliation of h-BN (1-2 um) in DMF, mixing with epoxy/593, curing')
rows_D = []
r = dict(common_D)
r.update(filler_material='BNNS', filler_material_original='BNNSs (from h-BN, 1-2 um)', filler_shape='nanosheet',
         filler_mean_size_um='1', filler_loading_vol_pct='25', filler_loading_original_value='25',
         filler_loading_original_unit='vol%', k_composite_W_mK='1.13', k_original_value='1.13',
         k_original_unit='W m-1 K-1', source_location='Table 1 row this paper (25vol% BNNSs)',
         notes='Neat epoxy k=0.18 W m-1 K-1 reported in text. BNNS 25 vol%.')
rows_D.append(r)
r = dict(common_D)
r.update(filler_material='BNNS', filler_material_original='AgNPs-BNNSs hybrid', filler_shape='nanosheet',
         filler_mean_size_um='1', filler_loading_vol_pct='25', filler_loading_original_value='25',
         filler_loading_original_unit='vol%', k_composite_W_mK='2.14', k_original_value='2.14',
         k_original_unit='W m-1 K-1', source_location='Table 1 row this paper (25vol% AgNPs-BNNSs); confirmed in text',
         notes='Ag nanoparticle decorated BNNS, 25 vol% total binary nanofiller. Fig 3a has full k vs content curves for EP-BN and EP-AgBN (0-25 vol%) not tabulated.')
rows_D.append(r)
n4, p4 = append_rows(D, rows_D, dict(candidate_id='P004', doi=D['doi'], paper_title=D['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym12020426.txt',
    tables_inspected='Table 1 (thermal conductivity comparison incl. this-paper rows)',
    figures_inspected='Figure 3a referenced (k vs content curves; not digitized)',
    candidate_measurements=2, unit_conversions='none (already W/mK family)',
    duplicate_checks='Table 1 literature rows excluded (not original measurements of this paper)',
    qc_findings='only this-paper rows extracted; Figure 3a curves not digitized'))

print(f'BATCH1 totals appended: A={n1} B={n2} C={n3} D={n4}  grand={n1+n2+n3+n4}')
