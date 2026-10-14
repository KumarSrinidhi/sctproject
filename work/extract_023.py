import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3A: 10.3390/nano13152243 (Nanomaterials 2023, 13, 2243) =====
# Own data in text (Sec. 3.3): neat epoxy TC 0.2; 30 wt% Al2O3@Graphene composite TC 0.97 W m-1 K-1.
# Other loadings (10/20 wt%) only in Figure 7a -> not extracted (no absolute value in text).
P = dict(doi='10.3390/nano13152243', source_url='https://doi.org/10.3390/nano13152243',
         paper_title='Thermally Conductive and Electrically Insulating Epoxy Composites Filled with Network-like Alumina In Situ Coated Graphene',
         year=2023)

rows = [dict(
    matrix_polymer='Epoxy (E51) with curing agent 593 and diluent 501 (100:25:15)',
    curing_agent='593 curing agent + 501 diluent',
    filler_material='Al2O3/graphene hybrid',
    filler_material_original='Al2O3@Graphene-CTAB (network-like alumina in situ coated graphene sheets)',
    filler_shape='hybrid',
    functionalization='In situ Al2O3 coating from aluminium sulfate/NaOH (540 C, 3 h) with CTAB surfactant',
    filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
    k_matrix_W_mK='0.2',
    k_composite_W_mK='0.97', k_original_value='0.97', k_original_unit='W m-1 K-1',
    k_direction='unknown',
    measurement_method='Laser flash (DXF-500, TA Instruments) + DSC Cp; k = alpha x Cp x rho, room temperature',
    processing_method='Filler dispersed in resin with vacuum defoaming mixer, poured into PTFE mold, cure 180 min at 120 C',
    value_source='text', confidence='High',
    source_location='Sec. 3.3: "The TC of the pure epoxy resin was 0.2 W m-1 K-1, and the TC of the composite with 30 wt% filler reached 0.97 W m-1 K-1"; repeated "At 30 wt% mixed fillers, the TC of the epoxy composite reached 0.97 W m-1 K-1"',
    notes='Hybrid filler judged in scope under "epoxy + other ceramics": alumina is the continuous insulating phase (~75% of filler mass), graphene core noted explicitly. Only 30 wt% has an absolute k in text (10/20 wt% are figure-only and were NOT digitized). CTAB variant shows the higher TC at 30 wt%.'),
]

n, p = append_rows(P, rows, dict(
    candidate_id='P066', doi=P['doi'], paper_title=P['paper_title'],
    date_processed='2026-10-14', access_result='EPMC fullTextXML (already local: work/fulltext/10.3390_nano13152243.txt)',
    files_inspected='work/fulltext/10.3390_nano13152243.txt (file existed locally but had never been extracted)',
    tables_inspected='Table 1 (FEM simulation parameters, no TC of own samples)',
    figures_inspected='Figure 7a TC vs filler content - figure-only values not digitized',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='DOI had zero rows before this run',
    qc_findings='1 row; scope flag recorded in notes (Al2O3-coated graphene hybrid, ceramic-dominant)'))

print(f'BATCH23: nano13152243={n} rejected={p}')
