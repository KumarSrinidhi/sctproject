import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== FIX: X row rejected for non-numeric temperature 'RT' =====
XFIX = dict(doi='10.1007/s40820-022-00863-z', source_url='https://doi.org/10.1007/s40820-022-00863-z',
            paper_title='Vertically aligned SiC nanowires/BN network in cellulose aerogel for thermally conductive epoxy composites',
            year=2022)
r = dict(matrix_polymer='Epoxy resin (EP), cellulose aerogel (CA) scaffold', curing_agent='',
         filler_material='BN', filler_material_original='m-BN + m-SiC nanowires hybrid in vertically aligned CA (CA/0.10 m-SiC/1.8 m-BN)',
         filler_shape='other', functionalization='SiC nanowire hybrid',
         filler_alignment='vertically aligned',
         filler_loading_wt_pct='16.69', filler_loading_original_value='16.69', filler_loading_original_unit='wt%',
         k_composite_W_mK='2.21', k_original_value='2.21', k_original_unit='W m−1 K−1',
         k_direction='vertical', measurement_temperature_C='25',
         measurement_method='Hot Disk TPS 2500S (thermal constant analyzer); IR camera validation',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='Ice-template assisted freeze casting of CA, vacuum EP impregnation',
         source_location='Abstract + Eq(1) discussion: CA/0.10 m-SiC/1.8 m-BN/EP Kc = 2.21 W m-1 K-1 at 16.69 wt%',
         notes='Hybrid total 16.69 wt% (m-BN primary + m-SiC nanowires secondary). Pure EP stated only as 890% TCE, not numerically. Retry after non-numeric RT temperature rejection.')
n0, p0 = append_rows(XFIX, [r], dict(candidate_id='P024', doi=XFIX['doi'], paper_title=XFIX['paper_title'],
    date_processed='2026-10-13', access_result='PDF-to-text (Springer OA)',
    files_inspected='work/fulltext/10.1007_s40820-022-00863-z.txt',
    tables_inspected='none with k', figures_inspected='Fig k curves',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='retry of rejected 0e680d76-094',
    qc_findings='RT changed to 25 C for numeric validation'))

# ===== A1: 10.1186/1556-276x-9-643 (silane/plasma BNNP / epoxy) =====
A1 = dict(doi='10.1186/1556-276x-9-643', source_url='https://doi.org/10.1186/1556-276x-9-643',
          paper_title='Fabrication of epoxy-boron nitride platelet composites with high filler fraction and thermal conductivity',
          year=2014)
common_A1 = dict(matrix_polymer='Epoxy resin', curing_agent='',
                 filler_material='BN', filler_material_original='BNNPs (boron nitride nanoplatelets), 70 wt%',
                 filler_shape='platelet', filler_loading_wt_pct='70',
                 filler_loading_original_value='70', filler_loading_original_unit='wt%',
                 measurement_method='DZDR-S thermal conductivity tester (transient plane source), vertical direction',
                 k_direction='through-plane (vertical)', value_source='text', confidence='High',
                 k_matrix_W_mK='0.31',
                 processing_method='Near-zero-flow molding / high-fraction fabrication method')
rows_A1 = [
    dict(common_A1, functionalization='Silane coupling agent treated',
         k_composite_W_mK='5.24', k_original_value='5.24', k_original_unit='W/mK',
         source_location='Abstract + Results: silane-treated sample max 5.24 W/mK at 70 wt%',
         notes='Silane-treated BNNPs, 70 wt%. Pure epoxy reported 0.31 W/mK.'),
    dict(common_A1, functionalization='Plasma treatment',
         k_composite_W_mK='4.61', k_original_value='4.61', k_original_unit='W/mK',
         source_location='Results: plasma-treated sample ~4.61 W/mK at 70 wt%',
         notes='Plasma-treated BNNPs, 70 wt% (same loading pair for treatment comparison).'),
]
n1, p1 = append_rows(A1, rows_A1, dict(candidate_id='P027', doi=A1['doi'], paper_title=A1['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML (BMC)',
    files_inspected='work/fulltext/10.1186_1556-276x-9-643.txt',
    tables_inspected='composition tables', figures_inspected='k vs loading curves (values in text at 70 wt%)',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='lower loadings figure-only',
    qc_findings='2 rows (silane vs plasma pair at 70 wt%)'))

# ===== A2: 10.2109/jcersj.105.197 (AlN / alumina in epoxy) =====
A2 = dict(doi='10.2109/jcersj.105.197', source_url='https://doi.org/10.2109/jcersj.105.197',
          paper_title='Thermal conductivity of aluminum nitride and alumina particulate-filled epoxy resin (in Japanese, English abstract)',
          year=1997)
common_A2 = dict(matrix_polymer='Epoxy resin', curing_agent='',
                 measurement_method='Laser flash (TC-3000H-NC, Sinku-Riko), density by water displacement',
                 k_direction='unknown', value_source='text', confidence='High', k_matrix_W_mK='')
rows_A2 = [
    dict(common_A2, filler_material='AlN', filler_material_original='AlN particles (size series)',
         filler_shape='particle', functionalization='None',
         filler_loading_vol_pct='68.5', filler_loading_original_value='68.5', filler_loading_original_unit='vol%',
         k_composite_W_mK='7.15', k_original_value='7.15', k_original_unit='W/mK',
         source_location='Abstract + Results: AlN composite 7.15 W/mK at 68.5 vol%',
         notes='Max loading point. Fig 3 has full curve (figure-only). Filler particle size affects k (paper focus).'),
    dict(common_A2, filler_material='Al2O3', filler_material_original='alumina particles',
         filler_shape='particle', functionalization='None',
         filler_loading_vol_pct='63.8', filler_loading_original_value='63.8', filler_loading_original_unit='vol%',
         k_composite_W_mK='2.68', k_original_value='2.68', k_original_unit='W/mK',
         source_location='Abstract + Results: alumina composite <2.68 W/mK at 63.8 vol%',
         notes='"lower than 2.68" at 63.8 vol% (upper bound phrasing); treated as reported value with caveat.'),
]
n2, p2 = append_rows(A2, rows_A2, dict(candidate_id='P028', doi=A2['doi'], paper_title=A2['paper_title'],
    date_processed='2026-10-13', access_result='Full text (JCI/JCerS repository, PDF-derived txt)',
    files_inspected='work/fulltext/10.2109_jcersj.105.197.txt',
    tables_inspected='filler property tables (no k)', figures_inspected='Fig 3 curves',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='2 rows; alumina value is upper-bound phrasing (<2.68), flagged in notes; classic 1997 paper'))

# ===== A3: 10.3390/polym16223126 (vertically aligned BN / PDMS) =====
A3 = dict(doi='10.3390/polym16223126', source_url='https://doi.org/10.3390/polym16223126',
          paper_title='Shear-assisted vertically aligned BN/PDMS composites via repeat blade coating for thermal interface materials',
          year=2024)
r = dict(matrix_polymer='PDMS', curing_agent='',
         filler_material='BN', filler_material_original='h-BN platelets, vertically aligned (V-BP)',
         filler_shape='platelet', functionalization='None',
         filler_alignment='vertically aligned (repeat blade coating + flipping)',
         filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.24', k_original_value='1.24', k_original_unit='W/mK',
         k_direction='out-of-plane', measurement_temperature_C='25',
         measurement_method='LFA (NETZSCH LFA 467) at 25 C; IR camera validation',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='Repeat blade coating with flipping/cutting to align BN out-of-plane',
         source_location='Abstract + Results: V-BP 30 wt% -> out-of-plane 1.24 W/mK',
         notes='Optional matrix: PDMS (not epoxy). Coating velocity effect ~40% (parametric, not separate rows).')
n3, p3 = append_rows(A3, [r], dict(candidate_id='P029', doi=A3['doi'], paper_title=A3['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym16223126.txt',
    tables_inspected='composition tables', figures_inspected='k curves (values in text at 30 wt%)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='lit values (45.15, 12.1, 1.227) excluded',
    qc_findings='1 row, optional PDMS matrix, out-of-plane direction'))

print(f'BATCH8 appended: fix={n0} A1={n1} A2={n2} A3={n3} grand={n0+n1+n2+n3}')
