import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3B: 10.1002/pc.28534 (Polymer Composites 2024, 45(12), 11104-11111) =====
# Previously on unusable_sources (Wiley 403). Recovered via OA repository da.lib.kobe-u.ac.jp
# (Kobe University accepted manuscript). Own-data absolute k in text for AlN only
# (P3HT/graphene values are carbon fillers -> out of scope for this dataset).
P = dict(doi='10.1002/pc.28534', source_url='https://doi.org/10.1002/pc.28534',
         paper_title='Thermal conductivity of epoxy resin films doped with a polythiophene/graphene complex or aluminum nitride',
         year=2024)

rows = [dict(
    matrix_polymer='DGEBA epoxy (JER 828, Mitsubishi Chemical)',
    curing_agent='Methyltetrahydrophthalic anhydride HN-2200 + catalyst 2E4MZ-CN (epoxy/hardener/catalyst 50/49.8/0.2 by weight)',
    filler_material='AlN',
    filler_material_original='AlN powder (mean particle size 1.0 um, Tokuyama Corp.)',
    filler_shape='particle',
    functionalization='None (as received)',
    filler_mean_size_um='1.0',
    filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
    k_matrix_W_mK='',
    k_composite_W_mK='0.5', k_original_value='0.5', k_original_unit='W/(m*K)',
    k_direction='unknown',
    measurement_method='Periodic heating-temperature, Thermowave Analyzer TA3 (Bethel); kappa = alpha*rho*Cp; in-plane and out-of-plane diffusivity; films 210 um thick, cured 120 C 2 h between Al plates',
    processing_method='Filler stirred into epoxy/hardener/catalyst mix (1 h atmospheric + 1 h vacuum), cast between Al plates with 210 um Teflon spacer, cure 120 C 2 h',
    value_source='text', confidence='Medium',
    source_location='Sec. 3 (Results, Fig. 5d discussion): "An AlN content of 40 wt% resulted in a thermal conductivity of ca. 0.5 W/(m*K)"',
    notes='In-plane and out-of-plane almost equal (isotropic AlN distribution). Value given as "ca. 0.5" (approximate) -> Medium confidence. Neat epoxy baseline cited in intro is literature (~0.2 W/(m*K) [7]), so k_matrix left blank. P3HT/graphene (carbon) rows intentionally NOT extracted (out of dataset scope).'),
]

n, p = append_rows(P, rows, dict(
    candidate_id='P068', doi=P['doi'], paper_title=P['paper_title'],
    date_processed='2026-10-14',
    access_result='Direct OA host da.lib.kobe-u.ac.jp (Kobe Univ. Kernel accepted manuscript) - previously Wiley-blocked',
    files_inspected='work/fulltext/10.1002_pc.28534.txt',
    tables_inspected='Table (W/[m*K] axis labels in Fig. 5 only) - values from body text',
    figures_inspected='Figure 5d (AlN TC vs loading) - not digitized; text gives 40 wt% value',
    candidate_measurements=1, unit_conversions='W/(m*K) = W/(m K)',
    duplicate_checks='DOI was on unusable_sources.csv; zero rows existed',
    qc_findings='1 AlN row; P3HT/graphene (carbon) values excluded as out-of-scope; unusable_sources.csv needs action update for this DOI'))

print(f'BATCH25: pc.28534={n} rejected={p}')
