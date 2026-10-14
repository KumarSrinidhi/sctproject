import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== X: 10.1007/s40820-022-00863-z (m-BN + m-SiC / cellulose aerogel / epoxy) =====
X = dict(doi='10.1007/s40820-022-00863-z', source_url='https://doi.org/10.1007/s40820-022-00863-z',
         paper_title='Vertically aligned SiC nanowires/BN network in cellulose aerogel for thermally conductive epoxy composites',
         year=2022)
r = dict(matrix_polymer='Epoxy resin (EP), cellulose aerogel (CA) scaffold', curing_agent='',
         filler_material='BN', filler_material_original='m-BN + m-SiC nanowires hybrid in vertically aligned CA (CA/0.10 m-SiC/1.8 m-BN)',
         filler_shape='other', functionalization='SiC nanowire hybrid',
         filler_alignment='vertically aligned',
         filler_loading_wt_pct='16.69', filler_loading_original_value='16.69', filler_loading_original_unit='wt%',
         k_composite_W_mK='2.21', k_original_value='2.21', k_original_unit='W m−1 K−1',
         k_direction='vertical', measurement_temperature_C='RT',
         measurement_method='Hot Disk TPS 2500S (thermal constant analyzer), ISO-style transient; IR camera validation',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='Ice-template assisted freeze casting of CA, vacuum EP impregnation',
         source_location='Abstract + Eq(1) discussion: CA/0.10 m-SiC/1.8 m-BN/EP Kc = 2.21 W m-1 K-1 at 16.69 wt%',
         notes='Hybrid total 16.69 wt% (m-BN primary + m-SiC nanowires secondary). Pure EP stated as 890% enhancement (k not quoted numerically; ~0.22 implied but not extracted).')
n1, p1 = append_rows(X, [r], dict(candidate_id='P024', doi=X['doi'], paper_title=X['paper_title'],
    date_processed='2026-10-13', access_result='PDF-to-text (Springer OA)',
    files_inspected='work/fulltext/10.1007_s40820-022-00863-z.txt',
    tables_inspected='none with k', figures_inspected='Fig k curves (values partly in text)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='1 row; pure-EP k not numerically quoted (only TCE %)'))

# ===== Y: 10.3390/nano12183235 (BNNS/MWCNTs/SiO2/epoxy ternary) =====
Y = dict(doi='10.3390/nano12183235', source_url='https://doi.org/10.3390/nano12183235',
         paper_title='Synergistic BNNSs/MWCNTs/SiO2 fillers in epoxy with gradient design for enhanced thermal conductivity',
         year=2012)
r = dict(matrix_polymer='Epoxy resin', curing_agent='',
         filler_material='BNNS', filler_material_original='BNNSs (40 wt%) + SiO2 (0.5 wt%) + MWCNTs@AGE (0.5 wt%)',
         filler_shape='nanosheet', functionalization='MWCNTs AGE-grafted; SiO2@KH560',
         filler_loading_wt_pct='41', filler_loading_original_value='40', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.9372', k_original_value='0.9372', k_original_unit='W m−1 K−1',
         measurement_method='Thermal conductivity measurement (per text; 529% over epoxy 0.1762)', k_direction='unknown',
         value_source='text', confidence='Medium', k_matrix_W_mK='0.1762',
         processing_method='Gradient filler design + curing',
         source_location='Results text: BNNSs 40 wt% + 0.5% SiO2 + 0.5% MWCNTs@AGE -> 0.9372 W m-1 K-1',
         notes='wt% column = 41 total (40 BNNS + 0.5 SiO2 + 0.5 CNT); original recorded as 40 (BNNS base). Abstract quotes 0.9327 for BNNSs/MWCNTs/SiO2@KH560 variant - near-duplicate values, body value 0.9372 retained.')
n2, p2 = append_rows(Y, [r], dict(candidate_id='P025', doi=Y['doi'], paper_title=Y['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano12183235.txt',
    tables_inspected='tables with composition', figures_inspected='k gradient curves',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='abstract 0.9327 vs text 0.9372 - single row kept, discrepancy noted',
    qc_findings='ternary system (BNNS primary); only max-loading gradient row in text, BNNS-only series figure-only'))

# ===== Z: 10.3390/polym13234074 (AlN / D-GQDs-modified epoxy sheet) =====
Z = dict(doi='10.3390/polym13234074', source_url='https://doi.org/10.3390/polym13234074',
         paper_title='D-GQDs Modified Epoxy Resin Enhances the Thermal Conductivity of AlN/Epoxy Resin Thermally Conductive Composites',
         year=2016)
common_Z = dict(measurement_method='Hot Disk TPS2500 (transient plate heat source, ISO 22007-2)',
                k_direction='sheet plane (in-plane', value_source='text', confidence='High', k_matrix_W_mK='0.19',
                filler_material='AlN', filler_shape='particle',
                filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
                processing_method='Sheet casting 5 mm, cured 80 C 12 h')
rows_Z = [
    dict(common_Z, matrix_polymer='Epoxy (D-GQDs modified, DG-ER)', curing_agent='',
         filler_material_original='AlN in DG-ER (D-GQDs-grafted epoxy matrix)',
         functionalization='D-GQDs modify matrix (not filler)',
         k_composite_W_mK='1.31', k_original_value='1.31', k_original_unit='W·m−1·K−1',
         source_location='Results: AlN 20 wt% AlN/DG-ER sheet -> 1.31 W·m−1·K−1 (6.89x ER matrix)',
         notes='Matrix-modified system; neat ER sheet = 0.19 W·m−1·K−1. Sheet form (5 mm).'),
    dict(common_Z, matrix_polymer='Epoxy (ER, unmodified)', curing_agent='',
         filler_material_original='AlN in neat ER',
         functionalization='None',
         k_composite_W_mK='0.83', k_original_value='0.83', k_original_unit='W·m−1·K−1',
         source_location='Results: AlN 20 wt% AlN/ER sheet -> 0.83 W·m−1·K−1',
         notes='Control with unmodified ER matrix at same 20 wt% AlN.'),
]
n3, p3 = append_rows(Z, rows_Z, dict(candidate_id='P026', doi=Z['doi'], paper_title=Z['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13234074.txt',
    tables_inspected='composition tables (no k)', figures_inspected='lambda curves (values in text at 20 wt%)',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='higher loadings figure-only',
    qc_findings='2 rows at 20 wt%; DG-ER vs ER matrix comparison pair'))

print(f'BATCH7 appended: X={n1} Y={n2} Z={n3} grand={n1+n2+n3}')
