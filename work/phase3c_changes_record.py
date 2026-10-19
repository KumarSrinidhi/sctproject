import json, csv, os
from datetime import date

phase3_papers = [
    # (candidate_id, doi, rows, route)
    ('P064', '10.1039/c8ra10645b', 10, 'Phase 3A local re-grep + extract_021 (RSC Table 1; local fulltext)'),
    ('P065', '10.3390/polym10030277', 2, 'Phase 3A local re-grep + extract_022 (MDPI fulltext)'),
    ('P066', '10.3390/nano13152243', 1, 'Phase 3A local re-grep + extract_023 (MDPI fulltext)'),
    ('P067', '10.3740/mrsk.2023.33.12.503', 3, 'Phase 3B direct OA fetch (journal.mrs-k.or.kr) + extract_024'),
    ('P068', '10.1002/pc.28534', 1, 'Phase 3B direct OA fetch (kobe-u repository) + extract_025'),
    ('P069', '10.1360/ssc-2022-0226', 10, 'Phase 3B direct OA fetch (scichina.com) + extract_026'),
    ('P070', '10.1002/pc.29136', 1, 'Phase 3C abstract harvest (Semantic Scholar/CORE) + extract_027'),
    ('P071', '10.1007/s10854-024-13657-3', 2, 'Phase 3C abstract harvest'),
    ('P072', '10.1088/1361-6463/ae6b9b', 1, 'Phase 3C abstract harvest'),
    ('P073', '10.1002/slct.202507155', 2, 'Phase 3C abstract harvest'),
    ('P074', '10.1063/5.0205196', 1, 'Phase 3C abstract harvest'),
    ('P075', '10.1002/app.55612', 1, 'Phase 3C abstract harvest'),
    ('P076', '10.1063/5.0211580', 1, 'Phase 3C abstract harvest'),
    ('P077', '10.1039/d4dt00979g', 3, 'Phase 3C abstract harvest'),
    ('P078', '10.1016/j.compscitech.2020.108304', 2, 'Phase 3C abstract harvest'),
    ('P079', '10.1016/j.apsusc.2020.147091', 1, 'Phase 3C abstract harvest'),
    ('P080', '10.1177/0021998320942575', 1, 'Phase 3C abstract harvest (liquid epoxy matrix flagged)'),
    ('P081', '10.1002/adfm.201900412', 1, 'Phase 3C abstract harvest'),
    ('P082', '10.1016/j.compscitech.2020.108322', 2, 'Phase 3C abstract harvest'),
    ('P083', '10.1016/j.compositesb.2020.107855', 1, 'Phase 3C abstract harvest'),
    ('P084', '10.1177/09540083211046456', 1, 'Phase 3C abstract harvest'),
    ('P085', '10.1177/09673911221110143', 1, 'Phase 3C abstract harvest (Ag hybrid excluded)'),
    ('P086', '10.1016/j.cej.2018.04.196', 1, 'Phase 3C abstract harvest'),
    ('P087', '10.1002/pc.28316', 1, 'Phase 3C abstract harvest (temperature ambiguous, flagged)'),
    ('P088', '10.1002/pc.27985', 2, 'Phase 3C abstract harvest'),
    ('P089', '10.1016/j.jcomc.2020.100087', 2, 'Phase 3C abstract harvest'),
    ('P090', '10.1063/1.5121349', 1, 'Phase 3C abstract harvest'),
    ('P091', '10.1080/15440478.2021.1966568', 1, 'Phase 3C abstract harvest'),
    ('P092', '10.1002/smll.75841', 1, 'Phase 3C abstract harvest'),
    ('P093', '10.1002/pc.70149', 1, 'Phase 3C abstract harvest (Cu hybrid excluded)'),
]

changes = {
    'phase': '3 (RETRY)',
    'date': date.today().isoformat(),
    'baseline': {'rows': 173, 'papers': 63},
    'after': {'rows': 232, 'papers': 93},
    'new_papers': len(phase3_papers),
    'new_rows': sum(r for _, _, r, _ in phase3_papers),
    'per_paper': [dict(candidate_id=c, doi=d, rows=n, route=route) for c, d, n, route in phase3_papers],
    'decisions': [
        'Sci-Hub deliberately not used for any blocked DOI (copyright/piracy); recorded in unusable_sources.csv as (policy) row.',
        'Abstract-only extractions accepted with value_source=text, source_location=Abstract(...), confidence=Medium (24 papers, 32 rows).',
        'Carbon-dominant fillers (graphene, CNT, carbon fiber, graphite, nanodiamond-core) excluded; ceramic-dominant hybrids (Al2O3@graphene, BN/graphene GO-shell, BNNS@nanodiamond-shell) included with hybrid-scope notes.',
        'Metal-dominant hybrids (Ag, Cu) excluded; metal-only baselines not extracted.',
        'Neat-polymer baselines recorded as k_matrix_W_mK, never as own rows.',
        'Literature-comparison k values (other groups\' materials) excluded; only own-data values extracted.',
        'build_deliverables.py run first (protected), then unusable_sources.csv post-processed by separate script per protocol.',
        '3 rows (P086, P089 x2) flagged non-numeric filler_loading_original_value (~1.1, 44-45) but retained: original string kept in that field, normalized numeric loading present in vol/wt columns.',
    ],
    'not_recovered_full_text': [
        {'doi': '10.1002/pc.29136', 'reason': 'UPF/HANDLE repository DNS unreachable from this host'},
        {'doi': '10.1007/s10854-024-13657-3', 'reason': 'Springer bot-challenge page'},
        {'doi': '10.1002/pc.71726', 'reason': 'Wiley 403; abstract lacks absolute k+loading pair -> not extracted'},
        {'doi': '10.1002/pc.71558', 'reason': 'Wiley 403; bio-based non-standard epoxy matrix -> out of scope'},
        {'doi': '10.1016/j.ceramint.2021.10.063', 'reason': 'Abstract lacks total filler loading -> not extractable'},
        {'doi': '10.1002/pat.70120', 'reason': 'Wiley 403; abstract lacks loading; r-GO metal/carbon hybrid out of scope'},
    ],
    'scripts': [
        'work/phase3a_regrep.py', 'work/phase3a_regrep2.py',
        'work/phase3_fetch.py', 'work/phase3b_wave2.py',
        'work/phase3c_abstracts.py', 'work/phase3c_review.py', 'work/extract_027.py',
        'work/phase3c_unusable_update.py', 'work/phase3c_verify.py',
        'work/extract_021.py', 'work/extract_022.py', 'work/extract_023.py',
        'work/extract_024.py', 'work/extract_025.py', 'work/extract_026.py',
    ],
    'logs': [
        'work/phase3_fetch_log.json', 'work/phase3b_wave2_log.json',
        'work/phase3c_abstract_hits.json', 'work/extraction_log.jsonl',
    ],
}
json.dump(changes, open('work/phase3_changes.json', 'w', encoding='utf-8'), indent=2)
print('phase3_changes.json written; new_rows', changes['new_rows'], 'new_papers', changes['new_papers'])
