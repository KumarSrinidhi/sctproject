import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

# ===== E: 10.1038/srep04779 (Sci Rep 2014) AlN@PI/Epoxy =====
E = dict(doi='10.1038/srep04779', source_url='https://doi.org/10.1038/srep04779',
         paper_title='The use of polyimide-modified aluminum nitride fillers in AlN@PI/Epoxy composites with enhanced thermal conductivity for electronic encapsulation',
         year=2014)
rows_E = [dict(matrix_polymer='Epoxy (bisphenol A type, epoxy equivalent 0.51-0.54 mol/100g)',
               curing_agent='methyl hexahydrophthalic anhydride (MHHPA)',
               filler_material='AlN', filler_material_original='AlN@PI (polyimide-coated aluminum nitride)',
               filler_shape='other', functionalization='Polyimide coating on AlN',
               filler_mean_size_um='', filler_aspect_ratio='',
               k_composite_W_mK='2.03', k_original_value='2.03', k_original_unit='W/mK',
               filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
               k_direction='unknown', measurement_method='Steady-state heat-flow apparatus (ASTM D5470)',
               value_source='table', confidence='High',
               source_location='Table 1 our-work row (40 wt AlN@PI/Epoxy 2.03 W/mK); confirmed in text',
               notes='Table 1 also lists literature comparison rows (excluded). Fig 2 has k vs 10-40 wt% for AlN@PI/epoxy and AlN/epoxy (not digitized). Matrix epoxy; filler density not given so wt->vol not converted.')]
n5, p5 = append_rows(E, rows_E, dict(candidate_id='P005', doi=E['doi'], paper_title=E['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.1038_srep04779.txt',
    tables_inspected='Table 1 (thermal conductivity and dielectric of composites)',
    figures_inspected='Figure 2/3 referenced for k vs loading (not digitized)',
    candidate_measurements=1, unit_conversions='none',
    duplicate_checks='literature comparison rows in Table 1 excluded',
    qc_findings='1 high-confidence row extracted; lower loadings figure-only'))

# ===== F: 10.3390/polym10121412 (Polymers 2018) PI matrix =====
F = dict(doi='10.3390/polym10121412', source_url='https://doi.org/10.3390/polym10121412',
         paper_title='Synergistic Improvement in Thermal Conductivity of Polyimide Nanocomposite Films Using Boron Nitride Coated Copper Nanoparticles and Nanowires',
         year=2018)
rows_F = [dict(matrix_polymer='Polyimide (from benzophenone-3,3 dicarboxylic acid / p-phenylenediamine, PEPA)',
               curing_agent='',
               filler_material='BN', filler_material_original='(CuNPs-CuNWs)@BN hybrid (BN-coated Cu nanoparticles and nanowires)',
               filler_shape='other', functionalization='BN coating on Cu NPs/NWs',
               k_composite_W_mK='4.32', k_original_value='4.32', k_original_unit='W/mK',
               filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
               k_direction='unknown', measurement_method='Laser flash ( Netzsch LFA 447 HyperFlash); in-plane and cross-plane options reported in paper',
               value_source='table', confidence='High',
               source_location='Table 1 this-work row (10 wt % 4.32 W/mK); confirmed in text',
               notes='Optional matrix category: polyimide. Hybrid filler dominated by Cu NWs; BN serves as coating. Direction of the 4.32 value not unambiguously mapped in table; paper studies oriented films.')]
n6, p6 = append_rows(F, rows_F, dict(candidate_id='P006', doi=F['doi'], paper_title=F['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym10121412.txt',
    tables_inspected='Table 1 (k and dielectric features incl. this-work row)',
    figures_inspected='', candidate_measurements=1, unit_conversions='none',
    duplicate_checks='literature rows excluded', qc_findings='1 row, optional matrix (PI); hybrid Cu/BN filler'))

# ===== G: 10.3390/polym13244417 (Polymers 2021) BN/AgNWs/EP =====
G = dict(doi='10.3390/polym13244417', source_url='https://doi.org/10.3390/polym13244417',
         paper_title='Nanoarchitectonics of BN/AgNWs/Epoxy Composites with High Thermal Conductivity and Electrical Insulation',
         year=2021)
common_G = dict(matrix_polymer='Epoxy (bisphenol A type)', curing_agent='MHHPA + MNA',
                filler_material='h-BN', filler_material_original='KH550-modified h-BN nanoplates + AgNWs',
                filler_shape='platelet', functionalization='Silane KH550 (on BN); PDA treatment mentioned for AgNWs',
                filler_loading_vol_pct='20', filler_loading_original_value='20', filler_loading_original_unit='vol%',
                k_direction='unknown', measurement_method='',
                value_source='table', confidence='High',
                processing_method='Fillers dispersed in epoxy, MHHPA/MNA curing, vacuum at 90 C',
                k_matrix_W_mK='',
                source_location='')
rows_G = []
for samp, ag, k in [('BN/Ag-0/EP', '0:300 AgNWs:BN mass ratio', 0.347),
                    ('BN/Ag-1/EP', '1:300 AgNWs:BN mass ratio', 0.352),
                    ('BN/Ag-4/EP', '4:300 AgNWs:BN mass ratio', 0.374)]:
    r = dict(common_G)
    r.update(k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W/mK',
             source_location=f'Table 4 this-research column, sample {samp}',
             notes=f'Sample {samp}: BN added at 20 vol% of epoxy; AgNWs:BN mass ratio {ag}. Measurement method not stated in extracted text. Table 4 Case1/Case2 columns are literature (excluded).')
    rows_G.append(r)
n7, p7 = append_rows(G, rows_G, dict(candidate_id='P007', doi=G['doi'], paper_title=G['paper_title'],
    date_processed='2026-10-13', access_result='EPMC fullTextXML',
    files_inspected='work/fulltext/10.3390_polym13244417.txt',
    tables_inspected='Table 4 (thermal conductivity comparison incl. this-research)',
    figures_inspected='', candidate_measurements=3, unit_conversions='none',
    duplicate_checks='Table 4 literature columns excluded', qc_findings='measurement method unreported in extracted text; AgNWs are secondary hybrid component'))

print(f'BATCH2 appended: E={n5} F={n6} G={n7} grand={n5+n6+n7}')
