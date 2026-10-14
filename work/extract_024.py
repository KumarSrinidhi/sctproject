import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3B: 10.3740/mrsk.2023.33.12.503 (Korean J. Mater. Res. 2023, 33(12), 503-510) =====
# Recovered via direct OA host journal.mrs-k.or.kr (phase3_fetch route 'direct:journal.mrs-k.or.kr').
# Text absolute k: neat epoxy 0.2; h-BN max ~1.11; OH-BNNS 20 wt% 2.47; GMA-BNNS 20 wt% 3.40 (Wm-1 K-1).
P = dict(doi='10.3740/mrsk.2023.33.12.503',
         source_url='https://doi.org/10.3740/mrsk.2023.33.12.503',
         paper_title='Enhancing Thermal Conductivity in Epoxy Composites with Functionalized Boron Nitride Nanosheets',
         year=2023)

COMMON = dict(
    matrix_polymer='DGEBA epoxy (YD-128, Kukdo Chem.)',
    curing_agent='Modified aliphatic amine KH-602 (epoxy:hardener 100:25)',
    filler_shape='nanosheet (BNNS) / platelet (h-BN)',
    k_matrix_W_mK='0.2',
    k_direction='in-plane',
    measurement_method='Laser thermal diffusivity, ULVAC Laser-PIT-M2 (in-plane), thin film 30x5x0.3 mm, room temperature',
    value_source='text',
    confidence='High',
    processing_method='Filler sonicated in ethanol, 60 C 15 min to evaporate ethanol, Thinky mixer 1000 RPM + sonication; +KH-602, sonicate 30 min, degas, cast Teflon mold',
)

rows = [
    dict(COMMON,
         filler_material='h-BN', filler_material_original='h-BN powder (5 um average, 98%, M. K. Impex)',
         filler_mean_size_um='5',
         functionalization='None (as received)',
         filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.11', k_original_value='1.11', k_original_unit='Wm-1 K-1',
         source_location='Sec. 3: "the in-plane thermal conductivity of h-BN/epoxy improves gradually as the h-BN content increases, reaching a maximum thermal conductivity of approximately 1.11 Wm-1 K-1, as depicted in Fig. 8(a)"',
         notes='Loadings studied: 5/10/15/20 wt%; "maximum" attributed to the 20 wt% top of the series (highest content) - loading inferred from the series, value itself is stated in text.',
         confidence='Medium'),
    dict(COMMON,
         filler_material='BNNS', filler_material_original='OH-BNNS (hydroxylated BN nanosheets, sonication + hydrothermal)',
         filler_mean_size_um='',
         functionalization='Hydroxyl (OH) via sonication + hydrothermal treatment (200 C, 12 h, IPA)',
         filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
         k_composite_W_mK='2.47', k_original_value='2.47', k_original_unit='Wm-1 K-1',
         source_location='Sec. 3: "The OH-BNNS/epoxy composite, with 20 wt% OH-BNNS filler, surpasses h-BN/epoxy with an impressive thermal conductivity of about 2.47 Wm-1 K-1, marking a remarkable increase of approximately 223 % over h-BN/epoxy"',
         notes='Cross-check: 2.47/1.11 - 1 = 122%, not 223%; paper states 223% "over h-BN/epoxy" but 223% of h-BN = 2.47 (i.e., 223% relative level). Value as printed: 2.47.'),
    dict(COMMON,
         filler_material='BNNS', filler_material_original='GMA-BNNS (PGMA-grafted OH-BNNS, radical polymerization with GMA/AIBN)',
         functionalization='GMA graft polymerization on OH-BNNS (AIBN, 70 C, 24 h, NMP)',
         filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
         k_composite_W_mK='3.40', k_original_value='3.40', k_original_unit='Wm-1 K-1',
         source_location='Sec. 3: "The thermal conductivity eventually reaches 3.40 Wm-1 K-1 in the in-plane direction when 20 wt% of GMA-BNNS filler is incorporated into the epoxy... enhancement factor (EF) of approximately 16 concerning neat epoxy"',
         notes='Cross-check: 3.40/0.2 = 17 ~ EF ~16 (paper). Highest value in paper.'),
]

n, p = append_rows(P, rows, dict(
    candidate_id='P067', doi=P['doi'], paper_title=P['paper_title'],
    date_processed='2026-10-14',
    access_result='Direct OA host journal.mrs-k.or.kr (Phase 3B fetch, previously not extracted)',
    files_inspected='work/fulltext/10.3740_mrsk.2023.33.12.503.txt',
    tables_inspected='Fig. 8(a,b) not digitized - all values from body text',
    figures_inspected='Figure 8 conductivity vs loading',
    candidate_measurements=3, unit_conversions='Wm-1 K-1 = W/(m K)',
    duplicate_checks='DOI had zero rows before this run',
    qc_findings='3 rows; h-BN 20 wt% loading inferred from "maximum" of the 5-20 wt% series -> confidence Medium; other two explicit -> High'))

print(f'BATCH24: mrsk={n} rejected={p}')
