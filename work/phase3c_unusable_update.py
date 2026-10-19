import csv, io

# DOIs recovered in Phase 3 via abstract harvest (extract_027) or direct OA fetch (extract_021-026)
recovered_abstract = {
    '10.1002/pc.29136', '10.1007/s10854-024-13657-3', '10.1088/1361-6463/ae6b9b',
    '10.1002/slct.202507155', '10.1063/5.0205196', '10.1002/app.55612',
    '10.1063/5.0211580', '10.1039/d4dt00979g', '10.1016/j.compscitech.2020.108304',
    '10.1016/j.apsusc.2020.147091', '10.1177/0021998320942575', '10.1002/adfm.201900412',
    '10.1016/j.compscitech.2020.108322', '10.1016/j.compositesb.2020.107855',
    '10.1177/09540083211046456', '10.1177/09673911221110143', '10.1016/j.cej.2018.04.196',
    '10.1002/pc.28316', '10.1002/pc.27985', '10.1016/j.jcomc.2020.100087',
    '10.1063/1.5121349', '10.1080/15440478.2021.1966568', '10.1002/smll.75841',
    '10.1002/pc.70149',
}
recovered_direct = {'10.1002/pc.28534'}  # full text via direct OA host (Kobe Univ repository)

extra_notes = {
    '10.1002/pc.29136': 'UPF repository DNS unreachable from this host (ERR_NAME_NOT_RESOLVED)',
    '10.1007/s10854-024-13657-3': 'Springer bot-challenge page returned instead of PDF',
}

src = 'unusable_sources.csv'
with open(src, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

changed = 0
for r in rows:
    doi = r['doi']
    if doi in recovered_abstract:
        r['action'] = 'abstract-recovered (Phase 3C, extract_027, Medium confidence)'
        r['reason'] = r['reason'] + '; full text still blocked'
        if doi in extra_notes:
            r['reason'] += ' (' + extra_notes[doi] + ')'
        changed += 1
    elif doi in recovered_direct:
        r['action'] = 'recovered (Phase 3B direct OA fetch, Kobe Univ repository; extract_025)'
        r['reason'] = r['reason'] + '; recovered via non-Wiley OA mirror'
        changed += 1

# add a decision note row for Sci-Hub policy
rows.append({
    'doi': '(policy)',
    'reason': 'Sci-Hub deliberately NOT used for any blocked DOI in Phase 3 (copyright/piracy concerns)',
    'action': 'excluded by project decision; see work/phase3_changes.json',
})

with open(src, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['doi', 'reason', 'action'])
    w.writeheader()
    w.writerows(rows)

print('updated', changed, 'entries; total rows now', len(rows))
