import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== Phase 3A: 10.1039/c8ra10645b (RSC Adv. 2019) - Table 1 absolute k =====
# Table 1: "Thermal conductivity of epoxy resin and its composites"
# header: EP | EP/PBMG | 1 wt% | 3 wt% | 5 wt% | 7 wt% | 10 wt%   (W (m-1 K-1))
# h-BN : 0.191 0.192 0.199 0.232 0.267 0.308 0.372
# MBN  : (EP / EP/PBMG blank) 0.218 0.271 0.323 0.378 0.452
# cross-checks: 0.378/0.191 = 1.98 -> abstract "increased by 98% at 7 wt% MBN" ok;
#               (0.452-0.191)/0.191 = 1.37 and (0.372-0.191)/0.191 = 0.95 -> body text ok.
P_META = dict(doi='10.1039/c8ra10645b', source_url='https://doi.org/10.1039/c8ra10645b',
              paper_title='Enhanced toughness and thermal conductivity for epoxy resin with a core-shell structured polyacrylic modifier and modified boron nitride',
              year=2019)

COMMON = dict(
    matrix_polymer='Epoxy (E51) with 5 wt% PBMG core-shell modifier',
    curing_agent='MTA (methyl tetrahydrophthalic anhydride) + DMP-30',
    filler_loading_original_unit='wt%',
    k_matrix_W_mK='0.192',
    k_direction='unknown',
    measurement_method="TC 3000 Series thermal conductivity apparatus (Xi'an Xiaxi, transient hot-wire), room temperature",
    k_original_unit='W (m-1 K-1)',
    processing_method='Wet ball milling + sonication exfoliation of h-BN in benzyl benzoate (MBN series), blending with EP/PBMG, degassing, cure 90 C 1 h then 150 C 4 h',
    value_source='table',
    confidence='High',
)

rows = []
for wt, k in [(1, 0.199), (3, 0.232), (5, 0.267), (7, 0.308), (10, 0.372)]:
    rows.append(dict(COMMON,
        filler_material='h-BN',
        filler_material_original='h-BN platelets (Qingzhou Matt Kechuang, as received)',
        filler_shape='platelet', functionalization='None (as received)',
        filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
        k_composite_W_mK=k, k_original_value=k,
        source_location=f'Table 1 "Thermal conductivity of epoxy resin and its composites", row h-BN, column {wt} wt%',
        notes='EP/PBMG matrix (5 wt% PBMG). Table 1 also gives neat EP 0.191 and EP/PBMG 0.192 W (m-1 K-1) as baselines.'))

for wt, k in [(1, 0.218), (3, 0.271), (5, 0.323), (7, 0.378), (10, 0.452)]:
    rows.append(dict(COMMON,
        filler_material='BNNS',
        filler_material_original='MBN (h-BN exfoliated to nanosheets: wet ball milling 350 rpm in benzyl benzoate + 100 W sonication 12 h)',
        filler_shape='nanosheet',
        functionalization='Exfoliated to nanosheets (wet ball milling + sonication in benzyl benzoate)',
        filler_loading_wt_pct=str(wt), filler_loading_original_value=str(wt),
        k_composite_W_mK=k, k_original_value=k,
        source_location=f'Table 1 "Thermal conductivity of epoxy resin and its composites", row MBN, column {wt} wt%',
        notes='EP/PBMG matrix (5 wt% PBMG); MBN = modified/exfoliated boron nitride nanosheets verified by TEM/Raman/XRD. Text cross-check: 3 wt% MBN k = 0.271; 7 wt% MBN k = 0.378 (98% above neat EP 0.191); 10 wt% MBN k = 0.452.'))

n, p = append_rows(P_META, rows, dict(
    candidate_id='P064', doi=P_META['doi'], paper_title=P_META['paper_title'],
    date_processed='2026-10-14', access_result='EPMC fullTextXML (already local: work/fulltext/10.1039_c8ra10645b.txt)',
    files_inspected='work/fulltext/10.1039_c8ra10645b.txt (Phase 3A re-grep: unit form "W (m -1 K -1 )" was missed by Phase 1/2 regex)',
    tables_inspected='Table 1 thermal conductivity of neat EP, EP/PBMG and h-BN/MBN composites at 1-10 wt%',
    figures_inspected='Fig. 10 (improvement ratio, not used)',
    candidate_measurements=10, unit_conversions='none (values already W (m-1 K-1))',
    duplicate_checks='DOI had zero rows before this run; 15 Phase-2 dropped row_ids untouched',
    qc_findings='10 rows; 5 h-BN + 5 MBN (exfoliated); values cross-checked against abstract (98% rise) and body text (0.271/0.452/0.372)'))

print(f'BATCH21: c8ra10645b={n} rejected={p}')
