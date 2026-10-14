import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== FIX: 3 B3 Ni rows rejected for non-numeric original loading '30 AlN + 2 Ni' =====
B3FIX = dict(doi='10.3390/polym11121990', source_url='https://doi.org/10.3390/polym11121990',
             paper_title='Magnetically aligned nickel powder in AlN/epoxy composites with enhanced thermal conductivity',
             year=2019)
common = dict(matrix_polymer='Epoxy resin', curing_agent='',
              filler_material='AlN', filler_material_original='',
              filler_shape='particle', functionalization='None',
              filler_loading_vol_pct='32', filler_loading_original_value='32',
              filler_loading_original_unit='vol%',
              filler_alignment='Ni chains aligned by vertical magnetic field',
              measurement_method='Thermal conductivity measurement (per text; pure epoxy 0.2 W/mK)',
              k_direction='through-plane (vertical alignment)', value_source='text', confidence='High',
              k_matrix_W_mK='0.2')
rows = [
    dict(common, filler_material_original='AlN 30 vol% (1 um) + Ni 50 nm 2 vol%, magnetic alignment',
         k_composite_W_mK='1.401', k_original_value='1.401', k_original_unit='W/mK',
         source_location='Fig 5 discussion: Ni 50 nm -> 1.401 W/mK',
         notes='Total filler 32 vol% = 30 vol% AlN + 2 vol% Ni (50 nm).'),
    dict(common, filler_material_original='AlN 30 vol% (1 um) + Ni 1 um 2 vol%, magnetic alignment',
         k_composite_W_mK='1.474', k_original_value='1.474', k_original_unit='W/mK',
         source_location='Text + Fig 5: Ni 1 um -> 1.474 W/mK (max, +737% vs pure EP, +58% vs AlN-only)',
         notes='Total filler 32 vol% = 30 vol% AlN + 2 vol% Ni (1 um). Optimal Ni size.'),
    dict(common, filler_material_original='AlN 30 vol% (1 um) + Ni 10 um 2 vol%, magnetic alignment',
         k_composite_W_mK='1.445', k_original_value='1.445', k_original_unit='W/mK',
         source_location='Fig 5 discussion: Ni 10 um -> 1.445 W/mK',
         notes='Total filler 32 vol% = 30 vol% AlN + 2 vol% Ni (10 um).'),
]
n0, p0 = append_rows(B3FIX, rows, dict(candidate_id='P032', doi=B3FIX['doi'], paper_title=B3FIX['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym11121990.txt',
    tables_inspected='filler property tables', figures_inspected='Fig 5',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='retry of rejected b8850d43-116/117/118 (non-numeric 30 AlN + 2 Ni)',
    qc_findings='original loading made numeric (32 vol%), composition moved to filler_material_original/notes'))

# ===== C1: 10.3390/mi16040413 (electric-field oriented BNNS / epoxy) =====
C1 = dict(doi='10.3390/mi16040413', source_url='https://doi.org/10.3390/mi16040413',
          paper_title='The Influence of Microsecond Pulsed Electric Field and Direct Current Electric Field on the Orientation Angle of Boron Nitride Nanosheets and the Thermal Conductivity of Epoxy Resin Composites',
          year=2025)
common_C1 = dict(matrix_polymer='Epoxy resin (EP)', curing_agent='8.5 g curing agent + 0.2 g accelerator',
                 filler_material='BNNS', filler_material_original='BNNSs (10 wt%), electric-field oriented',
                 filler_shape='nanosheet', functionalization='None',
                 filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
                 measurement_method='LFA (Netzsch LAF467HT), through-thickness',
                 k_direction='through-plane', value_source='text', confidence='High', k_matrix_W_mK='0.191')
rows_C1 = [
    dict(common_C1, filler_alignment='oriented by microsecond pulsed EF (50 Hz, 1.5 us, 8 kV/mm)',
         k_composite_W_mK='0.352', k_original_value='0.352', k_original_unit='W/(m·K)',
         source_location='Abstract + Results: pulsed EF 8 kV/mm -> 0.352 W/(m·K), 1.84x pure EP (0.191)',
         notes='Pulsed-field oriented BNNS 10 wt%.'),
    dict(common_C1, filler_alignment='oriented by DC EF (70 V/mm)',
         k_composite_W_mK='0.364', k_original_value='0.364', k_original_unit='W/(m·K)',
         source_location='Abstract: DC 70 V/mm -> 0.364 W/(m·K), 1.91x pure EP',
         notes='DC-field oriented BNNS 10 wt%.'),
]
n1, p1 = append_rows(C1, rows_C1, dict(candidate_id='P033', doi=C1['doi'], paper_title=C1['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_mi16040413.txt',
    tables_inspected='none with k', figures_inspected='k vs field curves (values quoted in abstract/text)',
    candidate_measurements=2, unit_conversions='none', duplicate_checks='lit values (0.588, 0.453, 1.148, 1.54) excluded',
    qc_findings='2 rows; processing param = electric field orientation (pulsed vs DC pair)'))

print(f'BATCH10 appended: fix={n0} C1={n1} grand={n0+n1}')
