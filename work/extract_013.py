import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# Retry rejected AlN-BN hybrid row without non-numeric size
E1fix = dict(doi='10.3390/polym14142950', source_url='https://doi.org/10.3390/polym14142950',
             paper_title='Highly Thermally Conductive Epoxy Composites with AlN/BN Hybrid Filler as Underfill Encapsulant Materials',
             year=2022)
r = dict(matrix_polymer='Epoxy', curing_agent='150 C 4-5 h',
         filler_material='AlN/BN hybrid',
         filler_material_original='AlN (spherical, 55 um) + BN flakes (35 um) hybrid, 75 wt% total',
         filler_shape='hybrid',
         filler_loading_wt_pct='75', filler_loading_original_value='75', filler_loading_original_unit='wt%',
         k_composite_W_mK='10.18', k_original_value='10.18', k_original_unit='W/(m K)',
         measurement_method='TPS 2500 S Hot Disk thermal constant analyzer, room temp (mean of 5 measurements)',
         k_direction='unknown', value_source='text', confidence='High',
         processing_method='Centrifugal mixing, cure 150 C 4-5 h',
         source_location='Abstract: TC = 10.18 W/(m K) at 75 wt% AlN-BN hybrid',
         notes='Best value, ~46x matrix. AlN 55 um, BN 35 um (sizes in filler_material_original). Hybrid ratio study at fixed 50 wt% is figure-only.')
n1, p1 = append_rows(E1fix, [r], dict(candidate_id='P038', doi=E1fix['doi'], paper_title=E1fix['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym14142950.txt',
    tables_inspected='Table 1 materials', figures_inspected='Fig 4c',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='retry of rejected hybrid row (non-numeric size removed)',
    qc_findings='retry only'))

# ===== E6: 10.3390/nano8120997 (h-BN + f-CNT / epoxy-cyanate ester) =====
E6 = dict(doi='10.3390/nano8120997', source_url='https://doi.org/10.3390/nano8120997',
          paper_title='Synergistic Effects of Functionalized CNTs and h-BN on Enhanced Thermal Conductivity of Epoxy/Cyanate Ester Composites',
          year=2018)
rows = []
for loading, kval, note in [
    ('0', '0.54', 'h-BN 40 wt% baseline (per previous work value quoted in this paper: resin matrix with h-BN 40 wt% = 0.54 W/mk)'),
    ('0.3', '0.648', 'h-BN 40 wt% + 0.3 wt% f-CNTs'),
    ('0.5', '0.745', 'h-BN 40 wt% + 0.5 wt% f-CNTs; 1.38x BN-only, +38%'),
]:
    rows.append(dict(
        matrix_polymer='Epoxy/cyanate ester blend',
        curing_agent='',
        filler_material='h-BN', filler_material_original=f'h-BN 40 wt% + functionalized CNTs {loading} wt%',
        functionalization='f-CNTs (functionalized CNTs co-filler)',
        filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt% h-BN (+ co-filler)',
        k_composite_W_mK=kval, k_original_value=kval, k_original_unit='W/mk',
        measurement_method='Thermal conductivity measurement (per paper; Agari model also applied)',
        k_direction='unknown', value_source='text', confidence='Medium',
        processing_method='h-BN + f-CNT in epoxy/cyanate ester',
        source_location='Abstract/Results: ' + note,
        notes='Co-filler system (h-BN + functionalized CNT). 40 wt% h-BN fixed; CNT loading varies. Matrix is epoxy/cyanate ester blend.'))
n2, p2 = append_rows(E6, rows, dict(candidate_id='P043', doi=E6['doi'], paper_title=E6['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano8120997.txt',
    tables_inspected='property tables', figures_inspected='k figures',
    candidate_measurements=3, unit_conversions='none',
    duplicate_checks='0.54 quoted as previous-work value for 40 wt% h-BN — Medium confidence as secondary citation within same paper series',
    qc_findings='3 rows; hybrid BN+CNT filler; matrix epoxy/cyanate ester blend'))

print(f'FIX+BATCH13 partial: E1fix={n1} E6={n2} grand={n1+n2}')
