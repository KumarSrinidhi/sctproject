# NEW FILE (audit-only). Finalizes work/audit_phase1_rows.json by layering manual
# verification findings (from context-level fulltext reading + Crossref title checks)
# on top of the automated evidence-check statuses. Does not modify any deliverable.
import json, csv

PATH = 'work/audit_phase1_rows.json'
data = json.load(open(PATH, encoding='utf-8'))
rows = {r['row_id']: r for r in data['rows']}
ds = {r['row_id']: r for r in csv.DictReader(open('thermal_conductivity_dataset.csv', encoding='utf-8-sig'))}

def add(rid, status, finding):
    r = rows[rid]
    r['findings'] = [f for f in r.get('findings', []) if f != finding]
    r['findings'].append(finding)
    # never downgrade a worse status back to verified
    order = ['verified', 'verified_with_warning', 'duplicate_measurement',
             'incorrect_value', 'incorrect_unit', 'missing_value',
             'incorrect_sample_mapping', 'suspicious_value', 'not_verifiable',
             'out_of_scope']
    if status != r['verification_status']:
        if status in order and order.index(status) > order.index(r['verification_status']):
            r['verification_status'] = status
        elif status == 'duplicate_measurement':
            r['verification_status'] = status
        elif r['verification_status'] == 'verified':
            r['verification_status'] = status

# ---- 1. Wrong paper_title vs Crossref (11 papers; values/DOI verified correct) ----
WRONG_TITLE = {
    '10.1038/s41598-018-19945-3': 'Enhanced Thermal Conductivity of Polyimide Composites with Boron Nitride Nanosheets',
    '10.3390/polym11121990': 'Effect of Particle Sizes of Nickel Powder on Thermal Conductivity of Epoxy Resin-Based Composites under Magnetic Alignment',
    '10.3390/polym11081335': 'Optimization of Boron Nitride Sphere Loading in Epoxy...',
    '10.3390/polym13030456': 'Thermal Properties of Surface-Modified and Cross-Linked Boron Nitride/Polyethylene Glycol Composite...',
    '10.3390/nano15120936': 'Preparation and Properties of Magnetically Responsive Graphene/Boron Nitride/Iron Oxide Filler Composite Epoxy...',
    '10.3390/polym18050648': 'Tailoring Flame Retardance and Thermal Conductivity of Epoxy/Benzoxazine Mixtures via Aluminum Trihydrate...',
    '10.1039/c8ra10211b': 'Improved dielectric stability of epoxy composites with ultralow boron nitride loading',
    '10.3390/ijms24098221': 'Boron Nitride/Polyurethane Composites with Good Thermal Conductivity and Flexibility',
    '10.3390/polym16081169': 'Enhancing Thermal Conductivity in Polymer Composites through Molding-Assisted Orientation of Boron Nitride Layers',
    '10.3390/polym17111507': 'Preparation of Phenolic Epoxy-Based Electronic Packaging Materials with High Thermal Conductivity...',
    '10.3390/nano8120997': 'Synergistic Effects of Functional CNTs and h-BN on Enhanced Thermal Conductivity of Epoxy/Cyanate Matrix Composites',
}
for rid, r in ds.items():
    if r['doi'] in WRONG_TITLE:
        add(rid, 'verified_with_warning',
            'paper_title in dataset is NOT the Crossref title of this DOI (actual: "%s"); '
            'DOI, k value and source_location verified correct against fulltext'
            % WRONG_TITLE[r['doi']][:80])

# ---- 2. a9d63e6e loading column stores formulation parts, not wt% ----
for rid in ['a9d63e6e-010','a9d63e6e-011','a9d63e6e-012','a9d63e6e-013',
            'a9d63e6e-014','a9d63e6e-015','a9d63e6e-016',
            'a9d63e6e-017','a9d63e6e-018','a9d63e6e-019','a9d63e6e-020',
            'a9d63e6e-021','a9d63e6e-022','a9d63e6e-023','a9d63e6e-024',
            'a9d63e6e-025','a9d63e6e-026','a9d63e6e-027','a9d63e6e-028',
            'a9d63e6e-029']:
    add(rid, 'incorrect_value',
        'filler_loading_wt_pct stores formulation parts (BN/(binder+BN) ratio, paper\'s own wording '
        '"70% by weight of BN with respect to combined weight of epoxy and BN"), not wt%% of total; '
        'paper states true composition 58.0 wt%% BN (=44.7 vol%%) for the -70 grade '
        '(and ~47 wt%% for -60); vol%% column is correct; k verified against source Table 2')

# ---- 3. Cross-paper duplicated measurements (companion papers, same samples) ----
CROSS_DUP = [
    # (drop_this_row, keep_this_row, note)
    ('a9d63e6e-014', 'd831a829-135', '3.34 W/mK ETLBN30-70 ambient-pressure sample; identical in both papers (polym13060955 Table 2 vs polym13020286 Table 1 S1)'),
    ('a9d63e6e-015', 'd831a829-136', '4.77 W/mK ETLBN30-70 175 kPa sample; identical in both papers (S2)'),
    ('a9d63e6e-016', 'd831a829-138', '7.67 W/mK ETLBN30-70 2 MPa sample; identical in both papers (S4)'),
    ('a8b6fee9-141', 'e5a9c8bd-122', '0.352 W/mK pulsed 8 kV/mm value cited from previous work by same group (mi16040413) into mi16101126; violates README literature-comparison exclusion'),
    ('a8b6fee9-142', 'e5a9c8bd-123', '0.364 W/mK DC 70 V/mm value cited from previous work by same group into mi16101126; violates README literature-comparison exclusion'),
]
for drop, keep, note in CROSS_DUP:
    add(drop, 'duplicate_measurement',
        'CROSS-PAPER duplicate of %s (%s). RECOMMEND DROP: %s' % (keep, note, drop))
    add(keep, 'duplicate_measurement',
        'CROSS-PAPER duplicate of %s (%s). RECOMMEND KEEP: %s' % (drop, note, keep))

# ---- 4. Out-of-scope / policy violations ----
add('4a11b03c-151', 'out_of_scope',
    'k=0.54 is explicitly a literature value from "our previous work" quoted in this paper '
    '(not data measured in nano8120997); README policy excludes literature-comparison values. '
    'RECOMMEND DROP or re-source to original DOI')
add('fa7ce3db-036', 'incorrect_sample_mapping',
    'filler_material="BN" mislabels a (CuNPs-CuNWs)@BN/PI hybrid film at 10 wt% (Cu-dominated '
    'hybrid, k=4.32); README requires hybrids to be labeled with "hybrid" in filler_material')
add('3bde4e56-147', 'incorrect_sample_mapping',
    'filler_material="cBN" with 0.0 wt% loading: this is the neat-matrix baseline row '
    'mislabeled as a cBN-filled composite')
add('544349ee-180', 'incorrect_sample_mapping',
    'filler_material="AlN" but source text and filler_material_original say trimodal '
    'Al2O3+BN (40 wt% total, 7.5 wt% BN) at k=1.64; "AlN" appears nowhere in the paper (0 hits)')

# ---- 5. Value not present in fulltext ----
add('b639a9c9-159', 'not_verifiable',
    'k=1.052 has 0 occurrences in fulltext (also absent: 1.05). Value is consistent with '
    '1.278/1.214=1.0527 derivation from the stated +21.4% vs AlN-only, or with digitization of '
    'Figure 5 (log says "TC figures" inspected); neither derivation nor digitization is disclosed '
    'in source_location ("Results: 30 wt% AlN = 1.052 W/m.K")')

# ---- 6. Documentation / labeling defects on specific rows ----
add('2f8abcf1-046', 'verified_with_warning',
    'curing_agent "Aradur 2954 (100:38)" conflicts with source (LY564/Aradur2954 = 100:35; '
    '100:38 is the LY5052/HY5052 ratio); notes typo "LY654" (paper: LY564)')
add('2f8abcf1-047', 'verified_with_warning',
    'curing_agent "Aradur 2954 (100:38)" conflicts with source (LY564/Aradur2954 = 100:35; '
    '100:38 is the LY5052/HY5052 ratio); notes typo "LY654" (paper: LY564)')
add('2a7dd240-105', 'verified_with_warning',
    'k_direction="through-plane" unsupported: paper states k at 5.32 vol% follows the in-plane '
    'model; also filler_loading_vol_pct=6.32 (text value) vs 6.33 in the paper table')
add('caf49a8d-129', 'verified_with_warning',
    'neat-matrix row (filler_material="none", 0 wt%) retained in a composite-measurement dataset; '
    'usable as baseline but out of the stated filler-composite scope')
add('0ab9ce56-184', 'verified_with_warning',
    'paper text internally inconsistent: one passage attributes 0.653 W/(m.K) to BN60/PU '
    'unordered, another to BN70/PU (0.545 vs 0.653 with +218.71%/+281.87% confirms 0.653=BN70); '
    'row follows BN70 attribution')
for rid, extra in [('4a11b03c-152', '0.3 wt% f-CNT'), ('4a11b03c-153', '0.5 wt% f-CNT')]:
    add(rid, 'verified_with_warning',
        'co-filler row (h-BN + %s) labeled filler_material="h-BN" without "hybrid", '
        'contrary to README hybrid-labeling convention; k verified against paper text' % extra)
add('031e3932-188', 'verified_with_warning',
    'co-filler row (60 wt% h-BN + 2 wt% CNT) labeled filler_material="BN" without "hybrid", '
    'contrary to README hybrid-labeling convention; k=1.10 verified against paper text')
add('f02bb9ff-095', 'verified_with_warning',
    'hybrid row (BNNS 40 + SiO2 0.5 + MWCNTs@AGE 0.5) labeled filler_material="BNNS" without '
    '"hybrid"; wt_pct=41 total vs original=40 documented in notes; k=0.9372 verified')

# ---- 7. Dropped recommendation summary already attached; recompute summary ----
import collections
summary = collections.Counter(r['verification_status'] for r in data['rows'])
data['summary'] = dict(summary)
data['summary']['total'] = len(data['rows'])
data['summary']['rows_with_findings'] = sum(1 for r in data['rows'] if r['findings'])
data['summary']['notes'] = (
    'Base statuses from automated evidence check (k-value string search + numeric-col scan); '
    'overrides/manual findings from context-level fulltext reading and Crossref title verification '
    'during Phase 1 audit. duplicate_measurement on BOTH sides of a pair; "RECOMMEND DROP/KEEP" '
    'text in findings names the row to drop.')
json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('final status counts:', json.dumps(dict(summary), indent=1))
print('rows with findings:', data['summary']['rows_with_findings'])
