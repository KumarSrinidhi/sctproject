import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== D1: 10.1039/d1ra08929c (MQ-modified spherical BN / silicone grease) =====
D1 = dict(doi='10.1039/d1ra08929c', source_url='https://doi.org/10.1039/d1ra08929c',
          paper_title='Liquid cooling system for battery modules with boron nitride based thermal conductivity silicone grease',
          year=2022)
common_D1 = dict(matrix_polymer='PDMS / silicone grease (MQ silicone resin modified)',
                 curing_agent='',
                 filler_material='BN', filler_shape='sphere',
                 measurement_method='TC-3000 thermal conductivity instrument',
                 k_direction='unknown', value_source='text', confidence='High',
                 processing_method='Spherical BN (SBN, self-made) modified with MQ silicone resin via sedimentation method, dispersed in PDMS')
rows_D1 = [
    dict(common_D1, filler_material_original='MQ@SBN (15 um spherical BN, 1.0 wt% MQ coating)',
         functionalization='MQ silicone resin coating (1.0 wt%)',
         filler_mean_size_um='15',
         filler_loading_wt_pct='70', filler_loading_original_value='70', filler_loading_original_unit='wt%',
         k_composite_W_mK='1.22', k_original_value='1.22', k_original_unit='W (m−1 K−1)',
         source_location='Abstract: HCSG TC = 1.22 W (m-1 K-1); Fig 6b caption: MQ dosage effect at filler content 70 wt%',
         notes='Best HCSG: 70 wt% MQ@SBN, 1.0 wt% MQ. TR = 0.49 C/W. 15 um SBN.'),
    dict(common_D1, filler_material_original='SBN (15 um spherical BN), no MQ',
         functionalization='None',
         filler_mean_size_um='15',
         filler_loading_wt_pct='70', filler_loading_original_value='70', filler_loading_original_unit='wt%',
         k_composite_W_mK='0.91', k_original_value='0.91', k_original_unit='W (m−1 K−1)',
         source_location='Results Fig 6b discussion: same filler content (70 wt%), SBN/PDMS = 0.91 vs MQ@SBN 1.22',
         notes='Control at 70 wt% without MQ modification.'),
]
n1, p1 = append_rows(D1, rows_D1, dict(candidate_id='P034', doi=D1['doi'], paper_title=D1['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML (RSC)',
    files_inspected='work/fulltext/10.1039_d1ra08929c.txt',
    tables_inspected='none with k', figures_inspected='Fig 6a/6b (values quoted in text)',
    candidate_measurements=2, unit_conversions='none',
    duplicate_checks='58 wt% triplet (0.81/0.95/1.11) excluded: sample-to-value mapping ambiguous in text',
    qc_findings='2 rows at 70 wt%; optional PDMS/silicone-grease matrix'))

# ===== D2: 10.3390/nano11020373 (BN / silicone-acrylate 3D-printed) =====
D2 = dict(doi='10.3390/nano11020373', source_url='https://doi.org/10.3390/nano11020373',
          paper_title='3D Printing of PDMS-Like Polymer Nanocomposites with Enhanced Thermal Conductivity: Boron Nitride Based Photocuring System',
          year=2021)
r = dict(matrix_polymer='Silicone acrylate (PDMS-like photocurable, TEGORAD 2800)', curing_agent='',
         filler_material='BN', filler_material_original='BN nanoparticles in silicone-acrylate (formulation 5 BN)',
         filler_shape='nanoparticle', functionalization='None',
         filler_loading_wt_pct='4.76', filler_loading_original_value='5', filler_loading_original_unit='phr (4.76 wt%)',
         k_composite_W_mK='0.215', k_original_value='0.215', k_original_unit='W/mK',
         measurement_method='Experimental k of printed sample (hot-plate + thermo-camera setup; matrix k set by experimental measurement 0.165 W/mK)',
         k_direction='unknown', value_source='text', confidence='Medium',
         processing_method='DLP vat photopolymerization (3D printing), UV cured',
         source_location='Results: experimental value of 5 BN -> 0.215 W/mK (matrix 0.165 W/mK)',
         notes='5 phr BN (4.76 wt%). Theoretical law-of-mixture bounds 12.1-14.4 W/mK NOT extracted (model). Optional matrix: silicone acrylate.')
n2, p2 = append_rows(D2, [r], dict(candidate_id='P035', doi=D2['doi'], paper_title=D2['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_nano11020373.txt',
    tables_inspected='formulation tables', figures_inspected='Fig 8 (k vs BN content)',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='theoretical 12.1-14.4 W/mK excluded (not experimental)',
    qc_findings='1 experimental row; other BN loadings (1-4 phr) figure-only'))

# ===== D3: 10.3390/polym13020248 (BN@AgNW / PDMS) =====
D3 = dict(doi='10.3390/polym13020248', source_url='https://doi.org/10.3390/polym13020248',
          paper_title='Enhanced the Thermal Conductivity of Polydimethylsiloxane via a Three-Dimensional Hybrid Boron Nitride@Silver Nanowires Thermal Network Filler',
          year=2021)
r = dict(matrix_polymer='PDMS', curing_agent='',
         filler_material='BN', filler_material_original='BN@15AgNWs hybrid (h-BN decorated with Ag nanowires, 15 mg/mL), 3D network',
         filler_shape='other', functionalization='AgNW in-situ growth on h-BN',
         filler_alignment='3D hybrid network',
         filler_loading_vol_pct='20', filler_loading_original_value='20', filler_loading_original_unit='vol%',
         k_composite_W_mK='0.914', k_original_value='0.914', k_original_unit='W/(m·K)',
         measurement_method='Thermal conductivity measurement (per text; 5.05x pure PDMS 0.18 W/mK)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='0.18',
         processing_method='In-situ growth of AgNWs on BN, 3D network filler in PDMS',
         source_location='Abstract: 20 vol% BN@15AgNWs/PDMS = 0.914 W/(m·K)',
         notes='Optional matrix: PDMS (not epoxy). 23% higher than plain BN/PDMS at same loading (control value not numeric). AgNW secondary component.')
n3, p3 = append_rows(D3, [r], dict(candidate_id='P036', doi=D3['doi'], paper_title=D3['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13020248.txt',
    tables_inspected='formulation tables', figures_inspected='Fig 5 (k vs AgNW content)',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='29.2 W/mK AgNW film value is literature [25] - excluded',
    qc_findings='1 row, optional PDMS matrix'))

# ===== D4: 10.3390/polym12092080 (h-BN/CNF in epoxy-impregnated paper) =====
D4 = dict(doi='10.3390/polym12092080', source_url='https://doi.org/10.3390/polym12092080',
          paper_title='Dielectric and Thermal Conductivity Characteristics of Epoxy Resin-Impregnated H-BN/CNF-Modified Insulating Paper',
          year=2020)
r = dict(matrix_polymer='Epoxy resin-impregnated insulating paper (RIP)', curing_agent='',
         filler_material='h-BN', filler_material_original='h-BN (10 wt%) + nano-CNF (0.1 wt%) on paper, epoxy impregnated',
         filler_shape='platelet', functionalization='CNF co-filler (0.1 wt%)',
         filler_loading_wt_pct='10.1', filler_loading_original_value='10', filler_loading_original_unit='wt% h-BN (+0.1 wt% CNF)',
         k_composite_W_mK='0.29', k_original_value='0.29', k_original_unit='W/m·K',
         measurement_method='Thermal conductivity measurement (per paper; RIP samples)', k_direction='unknown',
         value_source='text', confidence='High', k_matrix_W_mK='',
         processing_method='h-BN+CNF coated on insulating paper, vacuum epoxy impregnation',
         source_location='Conclusions: 0.1 wt% CNFs + 10 wt% h-BN/RIP -> 0.29 W/m.K',
         notes='Composite matrix = epoxy-impregnated paper (anisotropic system). 15-30 wt% h-BN variants: k not quoted in text (figure-only).')
n4, p4 = append_rows(D4, [r], dict(candidate_id='P037', doi=D4['doi'], paper_title=D4['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym12092080.txt',
    tables_inspected='dielectric tables', figures_inspected='k figures',
    candidate_measurements=1, unit_conversions='none', duplicate_checks='none needed',
    qc_findings='1 row; system is epoxy-impregnated paper (flagged in notes)'))

print(f'BATCH11 appended: D1={n1} D2={n2} D3={n3} D4={n4} grand={n1+n2+n3+n4}')
