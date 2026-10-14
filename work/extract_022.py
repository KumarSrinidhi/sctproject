import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3A: 10.3390/polym10030277 (Polymers 2018, 10, 277) =====
# Own-data absolute k stated in text (abstract, Sec. 3.5 and conclusions):
#   0.97 W/K.m at 40 wt% BN (6 um platelets)  ~400% above neat thiol-epoxy
#   1.75 W/K.m at 40 wt% BN as 80 um agglomerates (formulation "40 (80 um)" in Table 1)
M = dict(doi='10.3390/polym10030277', source_url='https://doi.org/10.3390/polym10030277',
         paper_title='Thermoconductive Thermosetting Composites Based on Boron Nitride Fillers and Thiol-Epoxy Matrices',
         year=2018)

COMMON = dict(
    matrix_polymer='Cycloaliphatic thiol-epoxy (ECC ERL-421D + PETMP)',
    curing_agent='PETMP (pentaerythritol tetrakis(3-mercaptopropionate)) + 1 phr DMAP',
    filler_material='h-BN',
    filler_shape='platelet',
    functionalization='None (as received)',
    filler_loading_wt_pct='40', filler_loading_original_value='40',
    filler_loading_original_unit='wt%',
    k_matrix_W_mK='',
    k_direction='unknown',
    measurement_method='Transient hot bridge (Linseis THB-100), room temperature',
    k_original_unit='W/K.m (= W/(m K))',
    processing_method='BN mixed into ECC/PETMP before curing; cure 120 C 1 h, 150 C 1 h, post-cure 200 C 0.5 h in aluminium molds',
    value_source='text',
    confidence='High',
)

rows = [
    dict(COMMON,
         filler_material_original='h-BN platelets (ESK TPC 006, 6 um average)',
         filler_mean_size_um='6',
         k_composite_W_mK='0.97', k_original_value='0.97',
         source_location='Sec. 3.5 + Conclusions: "at the proportion of 40% an increase of about 400% ... This value of thermal conductivity (0.97 W/K.m)"; "increase ... of about 400% (0.97 W/K.m) at the highest proportion added"',
         notes='Maximum BN loading = 40 wt% (highest proportion achieved; Sec. 3.4). Unit written W/K.m in paper = W/(m K).'),
    dict(COMMON,
         filler_material_original='h-BN agglomerates 80 um (Saint-Gobain PCTL5MHF)',
         filler_mean_size_um='80',
         k_composite_W_mK='1.75', k_original_value='1.75',
         source_location='Sec. 3.5 + Conclusions: "the value of 1.75 W/K.m (775% increase) has been reached" / "(1.75 W/K.m, 775% increase) if 80 um agglomerates were added"; loading = formulation "40 (80 um)" in Table 1',
         notes='Same 40 wt% BN loading but 80 um agglomerate grade. Unit written W/K.m in paper = W/(m K).'),
]

n, p = append_rows(M, rows, dict(
    candidate_id='P065', doi=M['doi'], paper_title=M['paper_title'],
    date_processed='2026-10-14', access_result='EPMC fullTextXML (already local: work/fulltext/10.3390_polym10030277.txt)',
    files_inspected='work/fulltext/10.3390_polym10030277.txt (Phase 3A re-grep caught non-standard unit "W/K.m")',
    tables_inspected='Table 1 formulation list (BN wt% 0/10/20/30/40 and "40 (80 um)"); Fig. 8 values not digitized',
    figures_inspected='Figure 8 (TC of neat + composites) - absolute values not needed, text gives 0.97 and 1.75',
    candidate_measurements=2, unit_conversions='W/K.m interpreted as W/(m K) (factor 1.0)',
    duplicate_checks='DOI had zero rows before this run',
    qc_findings='2 rows; both own data in text (High); literature values (0.97 ECC homopolymer, >2 W/K.m DGEBA-thiol, 1.04) excluded as comparisons'))

print(f'BATCH22: polym10030277={n} rejected={p}')
