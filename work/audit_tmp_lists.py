import csv
rows=list(csv.DictReader(open('thermal_conductivity_dataset.csv',encoding='utf-8-sig')))
print('=== k>=3.0 ===')
for r in sorted(rows,key=lambda r:-float(r['k_composite_W_mK'])):
    k=float(r['k_composite_W_mK'])
    if k>=3.0:
        ld=r['filler_loading_wt_pct'] or r['filler_loading_vol_pct']
        conf='M' if r['confidence']!='High' else 'H'
        print(f"{r['row_id']} {k:6.2f} {r['doi'][:36]:36} {r['filler_material'][:24]:24} {ld:>6} {conf}")
print()
print('=== Medium confidence ===')
for r in rows:
    if r['confidence']!='High':
        print(r['row_id'],r['doi'],r['k_composite_W_mK'],r['notes'][:100])
print()
print('=== k<=0.25 ===')
for r in sorted(rows,key=lambda r:float(r['k_composite_W_mK'])):
    k=float(r['k_composite_W_mK'])
    if k<=0.25:
        ld=r['filler_loading_wt_pct'] or r['filler_loading_vol_pct']
        print(f"{r['row_id']} {k:6.3f} {r['doi'][:36]:36} {r['filler_material'][:24]:24} {ld}")
