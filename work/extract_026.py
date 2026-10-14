import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3B: 10.1360/ssc-2022-0226 (SCIENTIA SINICA Chimica 2023, 53(2), 207-218) =====
# Recovered via direct OA host engine.scichina.com (Phase 3B fetch). Chinese-language paper.
# Table 1 (导热性能): k of FEP/GBN composites without and with hot pressing, W/(m K).
# GBN = BN/graphene hybrid filler (BNNS on graphene, PDDA-assisted).
P = dict(doi='10.1360/ssc-2022-0226', source_url='https://doi.org/10.1360/ssc-2022-0226',
         paper_title='Preparation of boron nitride/graphene composite thermal conductive filler and study on flame retardant, thermal conductivity and insulation properties of epoxy resin composites',
         year=2023)

COMMON = dict(
    matrix_polymer='Flame-retardant epoxy (FEP, lab-made): bisphenol-A epoxy resin + P-N synergistic additive flame retardant',
    curing_agent='DDM (4,4-diaminodiphenylmethane, stoichiometric)',
    filler_material='BN/graphene hybrid',
    filler_material_original='GBN (BN nanosheets on graphene; BN 1 um liquid-phase exfoliated in IPA 12 h + graphene, PDDA-assisted)',
    filler_shape='hybrid',
    functionalization='PDDA (polydiallyldimethylammonium chloride) surface treatment; BNNS exfoliated from 1 um BN',
    k_matrix_W_mK='0.217',
    k_direction='unknown',
    measurement_method='Laser flash analysis (LFA), NETZSCH LFA 467, GB/T 22588-2008; disc 12.6 mm diameter, 1-3 mm thick, room temperature',
    value_source='table',
    confidence='High',
    source_location='Table 1 "FEP/GBN composites thermal conductivity (W/(m K))" + text Sec. 3.3 (0.593 / 0.931 / 0.217 quoted in prose)',
)

NOCR = 'Filler dispersed in ethanol (sonication 40 min) + preheated FEP, stir 30 min, 100 C to remove ethanol, + molten DDM, mix 40 s, cast steel mold; conventional oven cure 120 C then 150 C, 2 h each (no pressure)'
HP = 'Same as no-hot-press but hot-press cure on hydraulic press: 120 C then 150 C, 2 h each, 10 MPa'

rows = []
for load, k_np, k_hp in [(1, 0.245, 0.273), (2, 0.341, 0.309), (3, 0.363, 0.524),
                         (4, 0.461, 0.699), (5, 0.593, 0.931)]:
    rows.append(dict(COMMON,
        filler_loading_wt_pct=str(load), filler_loading_original_value=str(load),
        filler_loading_original_unit='wt%',
        k_composite_W_mK=str(k_np), k_original_value=str(k_np), k_original_unit='W/(m K)',
        processing_method=NOCR,
        source_location=COMMON['source_location'] + f' - column 未热压 (no hot press), FEP/GBN {load}',
        notes='Conventional oven cure (no hot press).'))
    rows.append(dict(COMMON,
        filler_loading_wt_pct=str(load), filler_loading_original_value=str(load),
        filler_loading_original_unit='wt%',
        k_composite_W_mK=str(k_hp), k_original_value=str(k_hp), k_original_unit='W/(m K)',
        processing_method=HP,
        source_location=COMMON['source_location'] + f' - column 热压后 (after hot press), FEP/GBN {load}',
        notes='Hot-pressed at 10 MPa. At 2 wt% hot-press k (0.309) is below no-hot-press (0.341) as printed in Table 1.'))

n, p = append_rows(P, rows, dict(
    candidate_id='P069', doi=P['doi'], paper_title=P['paper_title'],
    date_processed='2026-10-14',
    access_result='Direct OA host engine.scichina.com (Phase 3B fetch, previously not extracted)',
    files_inspected='work/fulltext/10.1360_ssc-2022-0226.txt (Chinese full text)',
    tables_inspected='Table 1 (FEP/GBN thermal conductivity, both processing columns)',
    figures_inspected='Figure 6 (TC vs loading) - table values used',
    candidate_measurements=10, unit_conversions='W/(m K) = W/(m K)',
    duplicate_checks='DOI had zero rows before this run',
    qc_findings='10 composite rows (5 loadings x 2 processing routes); neat FEP 0.217 recorded as k_matrix (not as its own row, per dataset convention of composite-only rows)'))

print(f'BATCH26: ssc-2022-0226={n} rejected={p}')
