import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from io_append import append_rows

AB = 'Abstract (Semantic Scholar indexed publisher abstract; full text inaccessible)'

# Each entry: (candidate_id, paper_meta, [rows])
PAPERS = []

def add(cid, doi, title, year, rows):
    PAPERS.append((cid, dict(doi=doi, source_url='https://doi.org/' + doi,
                             paper_title=title, year=year), rows))

def row(**kw):
    base = dict(
        k_direction='unknown',
        measurement_method='Not stated in abstract',
        value_source='text', confidence='Medium',
        source_location=AB,
    )
    base.update(kw)
    return base

# ---- P070: pc.29136 ----
add('P070', '10.1002/pc.29136',
    'Enhancing directional thermal conductivity in hexagonal boron nitride reinforced epoxy composites through robust interfacial bonding',
    2024, [row(
        matrix_polymer='Epoxy (type not stated in abstract)',
        filler_material='h-BN',
        filler_material_original='h-BN plates, silane-modified + thermally treated',
        filler_shape='platelet',
        functionalization='Silane treatment after acid/thermal activation',
        filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
        k_matrix_W_mK='0.21',
        k_composite_W_mK='0.47', k_original_value='0.47', k_original_unit='W/mK',
        k_direction='through-thickness',
        source_location=AB + ': "increase in the epoxy\'s TC perpendicular to the plane, going from 0.21 to 0.47 (W/mK), showing a remarkable 123.8% enhancement by adding 10 wt% of silane-modified-thermal treated h-BN particles"',
        notes='Abstract-only (OA copy at UPF repository unreachable: DNS failure on this host). Cross-check 0.47/0.21-1=123.8% matches abstract.'),
    ])

# ---- P071: s10854-024-13657-3 ----
add('P071', '10.1007/s10854-024-13657-3',
    'Functionalization of boron nitride with poly(catechol-polyamine) and bis(gamma-triethoxysilylpropyl)tetrasulfide for epoxy composites',
    2024, [
        row(matrix_polymer='Bisphenol A-type epoxy (Ep)',
            filler_material='h-BN', filler_material_original='unmodified h-BN',
            filler_shape='platelet', functionalization='None (as received)',
            filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
            k_matrix_W_mK='0.200',
            k_composite_W_mK='0.817', k_original_value='0.817', k_original_unit='W/(m*K)',
            source_location=AB + ': "The heat conductivity of final BN/Ep composite achieved 0.817 W/(m·K) containing 30 wt% BN"',
            notes='Abstract-only (Springer PDF behind bot challenge).'),
        row(matrix_polymer='Bisphenol A-type epoxy (Ep)',
            filler_material='h-BN', filler_material_original='BN-PCPA-Si69 (poly(catechol-polyamine) + bis(gamma-triethoxysilylpropyl)tetrasulfide modified BN)',
            filler_shape='platelet',
            functionalization='Noncovalent PCPA + covalent Si69 silane coupling',
            filler_loading_wt_pct='30', filler_loading_original_value='30', filler_loading_original_unit='wt%',
            k_matrix_W_mK='0.200',
            k_composite_W_mK='0.881', k_original_value='0.881', k_original_unit='W/(m*K)',
            source_location=AB + ': "the heat conductivity of the composite (mBN/Ep) achieved 0.881 W/(m·K) containing 30 wt% BN-PCPA-Si69... compared to pure epoxy resin (0.200 W/(m·K))... increased by 364%"',
            notes='Abstract-only. Cross-check 0.881/0.200-1=340% (abstract states 364%; value 0.881 used as printed).'),
    ])

# ---- P072: ae6b9b ----
add('P072', '10.1088/1361-6463/ae6b9b',
    'Interface engineering of AlN via phosphoric acid modification for enhanced thermal conduction, electrical insulation and mechanical properties of epoxy composites',
    2025, [row(
        matrix_polymer='Epoxy (EP)',
        filler_material='AlN', filler_material_original='P-AlN (phosphoric acid modified aluminum nitride)',
        filler_shape='particle', functionalization='Phosphoric acid modification',
        filler_loading_wt_pct='35', filler_loading_original_value='35', filler_loading_original_unit='wt%',
        k_composite_W_mK='0.41', k_original_value='0.41', k_original_unit='W·m−1·K−1',
        source_location=AB + ': "at an optimal P-AlN loading of 35 wt%, the composite exhibits a thermal conductivity of 0.41 W·m−1·K−1, representing a 78.3% improvement over the pristine"',
        notes='Abstract-only (IOP host previously blocked).'),
    ])

# ---- P073: slct.202507155 ----
add('P073', '10.1002/slct.202507155',
    'Thermal Conductive, Dielectric, and Viscosity Properties of Multidimensional Hexagonal Boron Nitride/Aluminum Oxide/Epoxy Composites',
    2025, [
        row(matrix_polymer='Epoxy (EP)',
            filler_material='h-BN/Al2O3 hybrid', filler_material_original='multidimensional h-BN + spherical Al2O3 hybrid',
            filler_shape='hybrid', functionalization='None stated',
            filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
            k_composite_W_mK='0.827', k_original_value='0.827', k_original_unit='W/(m*K)',
            source_location=AB + ': "when the content of h-BN/Al2O3 was 20 wt%, the thermal conductivity reached 0.827 W/(m·K), which was 359.44% higher than that of pure EP"',
            notes='Abstract-only. Implied neat EP ~0.18 W/(m·K) (not extracted as k_matrix; derived).'),
        row(matrix_polymer='Epoxy (EP) + 3 wt% benzyl glycidyl ether (BGE) reactive diluent',
            filler_material='h-BN/Al2O3 hybrid', filler_material_original='multidimensional h-BN + spherical Al2O3 hybrid',
            filler_shape='hybrid', functionalization='None stated',
            filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
            k_composite_W_mK='0.796', k_original_value='0.796', k_original_unit='W/(m*K)',
            source_location=AB + ': "When the usage of BGE was 3 wt%, the viscosity of 20 wt% h-BN/Al2O3/EP suspension decreased from 13677 to 5301 mP·s, while its thermal conductivity still maintained at 0.796 W/(m·K)"',
            notes='Abstract-only; same filler system with BGE diluent.'),
    ])

# ---- P074: 10.1063/5.0205196 ----
add('P074', '10.1063/5.0205196',
    'Enhanced thermal conductivity of epoxy resin by incorporating three-dimensional boron nitride thermally conductive network',
    2023, [row(
        matrix_polymer='Epoxy (EP)',
        filler_material='BNNS', filler_material_original='BNNS@PU (BN nanosheets chemically bonded to polyurethane foam supporter)',
        filler_shape='nanosheet network', functionalization='Chemical bonding to PU foam scaffold',
        filler_loading_wt_pct='5.93', filler_loading_original_value='5.93', filler_loading_original_unit='wt%',
        k_composite_W_mK='0.521', k_original_value='0.521', k_original_unit='W/m K',
        source_location=AB + ': "the thermal conductivity of the BNNS@PU/EP composites reaches 0.521 W/m K with an enhancement rate of 30.89 at an ultra-low BNNS filler content (5.93 wt. %)"',
        notes='Abstract-only. Loading = BNNS content in composite (quantified by TGA).'),
    ])

# ---- P075: app.55612 ----
add('P075', '10.1002/app.55612',
    'Sugar-template method to construct a boron nitride filler network to enhance the thermal conductivity of epoxy',
    2020, [row(
        matrix_polymer='Epoxy (EP)',
        filler_material='h-BN', filler_material_original='h-BN honeycomb 3D skeleton (sugar template)',
        filler_shape='3D network', functionalization='None; sugar-templated honeycomb scaffold',
        filler_loading_vol_pct='52', filler_loading_original_value='52', filler_loading_original_unit='vol%',
        k_composite_W_mK='2.25', k_original_value='2.25', k_original_unit='W/m K',
        source_location=AB + ': "the composite for h-BN/EP reaches a TC of 2.25 W/m K when composed of 52 vol% h-BN"',
        notes='Abstract-only; laser flash measurement per abstract.'),
    ])

# ---- P076: 10.1063/5.0211580 ----
add('P076', '10.1063/5.0211580',
    'Significantly enhancing the through-plane thermal conductivity of epoxy dielectrics by constructing aramid nanofiber/boron nitride nanosheet framework',
    2023, [row(
        matrix_polymer='Epoxy dielectric',
        filler_material='BNNS', filler_material_original='ANF-BNNS (aramid nanofiber + BNNS collaborative vertical framework)',
        filler_shape='nanosheet network', functionalization='ANF hybridization (vacuum freeze-drying + impregnation)',
        filler_loading_vol_pct='1.43', filler_loading_original_value='1.43', filler_loading_original_unit='vol%',
        k_composite_W_mK='0.87', k_original_value='0.87', k_original_unit='W·m−1·K−1',
        k_direction='through-plane',
        source_location=AB + ': "The resultant ANF-BNNS/epoxy achieved a high through-plane of 0.87 W·m−1·K−1 at only 1.43 vol. % BNNS"',
        notes='Abstract-only; loading refers to BNNS fraction.'),
    ])

# ---- P077: d4dt00979g ----
def dnrow(fillermat, orig, funct, k, label):
    return row(matrix_polymer='Epoxy',
               filler_material=fillermat, filler_material_original=orig, filler_shape='platelet',
               functionalization=funct,
               filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt%',
               k_composite_W_mK=str(k), k_original_value=str(k), k_original_unit='W m-1 K-1',
               k_direction='in-plane',
               source_location=AB + f': "the DNBN/epoxy composite exhibited higher thermal conductivity (in-plane: 47.03 W m-1 K-1) at 60 wt% filler content compared to BN/epoxy (39.40 W m-1 K-1) and PNBN/epoxy (33 W m-1 K-1) composites"',
               notes='Abstract-only; %s; in-plane direction as stated.' % label)

add('P077', '10.1039/d4dt00979g',
    'Synchronously enhancing thermal conductivity and dielectric properties in epoxy composites via incorporation of surface-functionalized hexagonal boron nitride',
    2024, [
        dnrow('h-BN', 'unmodified microscale h-BN', 'None', 39.40, 'unmodified BN/epoxy baseline'),
        dnrow('h-BN', 'DNBN: h-BN functionalized with N-[3-(trimethoxysilyl)propyl]ethylene diamine (DN)',
              'Silane DN (N-[3-(trimethoxysilyl)propyl]ethylene diamine)', 47.03, 'DN-silane modified'),
        dnrow('h-BN', 'PNBN: h-BN functionalized with N-[3-(trimethoxysilyl)propyl]aniline (PN)',
              'Silane PN (N-[3-(trimethoxysilyl)propyl]aniline)', 33.0, 'PN-silane modified'),
    ])

# ---- P078: 10.1016/j.compscitech.2020.108304 ----
add('P078', '10.1016/j.compscitech.2020.108304',
    'Enhanced thermal conductivity of epoxy composites by constructing aluminum nitride honeycomb reinforcements',
    2020, [
        row(matrix_polymer='Epoxy (EP)',
            filler_material='AlN', filler_material_original='AlN-H (aluminum nitride honeycomb, freeze-cast)',
            filler_shape='honeycomb network', functionalization='None; freeze-cast honeycomb',
            filler_loading_vol_pct='47.26', filler_loading_original_value='47.26', filler_loading_original_unit='vol%',
            k_composite_W_mK='9.48', k_original_value='9.48', k_original_unit='W m−1 K−1',
            k_direction='parallel to AlN-H channels (in-plane-like)',
            source_location=AB + ': "maximal thermal conductivity values of 9.48 W m−1 K−1 and 4.45 W m−1 K−1 in the directions parallel and perpendicular to the AlN–H channels, respectively, at AlN loading of 47.26 vol%"',
            notes='Abstract-only.'),
        row(matrix_polymer='Epoxy (EP)',
            filler_material='AlN', filler_material_original='AlN-H (aluminum nitride honeycomb, freeze-cast)',
            filler_shape='honeycomb network', functionalization='None; freeze-cast honeycomb',
            filler_loading_vol_pct='47.26', filler_loading_original_value='47.26', filler_loading_original_unit='vol%',
            k_composite_W_mK='4.45', k_original_value='4.45', k_original_unit='W m−1 K−1',
            k_direction='perpendicular to AlN-H channels (through-plane-like)',
            source_location=AB + ': (same sentence as parallel value)',
            notes='Abstract-only; perpendicular direction.'),
    ])

# ---- P079: 10.1016/j.apsusc.2020.147091 ----
add('P079', '10.1016/j.apsusc.2020.147091',
    'Enhanced thermal conductivity of a polysilazane-coated A-BN/epoxy composite following surface treatment with silanes',
    2020, [row(
        matrix_polymer='Epoxy',
        filler_material='h-BN', filler_material_original='A-BN (spherical aggregated BN) coated with polysilazane + APTES',
        filler_shape='spherical aggregate', functionalization='PSZ coating + APTES silane',
        filler_loading_wt_pct='75', filler_loading_original_value='75', filler_loading_original_unit='wt%',
        k_composite_W_mK='11.8', k_original_value='11.8', k_original_unit='W m−1 K−1',
        source_location=AB + ': "An epoxy composite contained the BN surface modified with PSZ and APTES had the highest thermal conductivity of 11.8 W m−1 K−1 at a filler fraction of 75 wt%. Its thermal conductivity was 62 times higher than that of the neat epoxy."',
        notes='Abstract-only. Implied neat epoxy ~0.19 (not extracted).'),
    ])

# ---- P080: 10.1177/0021998320942575 ----
add('P080', '10.1177/0021998320942575',
    'Enhanced thermal conductivity of epoxy/alumina composite through multiscale-disperse packing',
    2020, [row(
        matrix_polymer='Liquid epoxy (uncured matrix measured)',
        filler_material='Al2O3', filler_material_original='spherical Al2O3, multiscale particle size distribution',
        filler_shape='particle', functionalization='None stated',
        filler_loading_vol_pct='79', filler_loading_original_value='79', filler_loading_original_unit='vol%',
        k_matrix_W_mK='0.28',
        k_composite_W_mK='6.7', k_original_value='6.7', k_original_unit='W m−1 K−1',
        measurement_method='Steady-state method, 25 C',
        measurement_temperature_C='25',
        source_location=AB + ': "The highest thermal conductivity of Al2O3-filled liquid epoxy measured by steady-state method is 6.7 W m−1 K−1 at 25 C, which is approximately 23 times higher than the neat epoxy (0.28 W m−1 K−1)."',
        notes='Abstract-only. IMPORTANT: k measured on LIQUID (uncured) epoxy; abstract notes 10-15% lower k for cured samples (value not given).'),
    ])

# ---- P081: 10.1002/adfm.201900412 ----
add('P081', '10.1002/adfm.201900412',
    'An Anisotropically High Thermal Conductive Boron Nitride/Epoxy Composite Based on Nacre-Mimetic 3D Network',
    2019, [row(
        matrix_polymer='Epoxy',
        filler_material='BNNS', filler_material_original='BNNS nacre-mimetic 3D network (bidirectional freezing)',
        filler_shape='nanosheet network', functionalization='None; bidirectional freeze-casting',
        filler_loading_vol_pct='15', filler_loading_original_value='15', filler_loading_original_unit='vol%',
        k_composite_W_mK='6.07', k_original_value='6.07', k_original_unit='W m−1 K−1',
        source_location=AB + ': "The as-prepared composite exhibits a high thermal conductivity (6.07 W m−1 K−1) at 15 vol% BNNS loading"',
        notes='Abstract-only; direction not specified in abstract (nacre-mimetic networks are typically anisotropic).'),
    ])

# ---- P082: 10.1016/j.compscitech.2020.108322 ----
add('P082', '10.1016/j.compscitech.2020.108322',
    'Bi-directional high thermal conductive epoxy composites with radially aligned boron nitride nanosheets lamellae',
    2020, [
        row(matrix_polymer='Epoxy',
            filler_material='BNNS', filler_material_original='radially aligned BNNS lamellae (radial freeze-casting)',
            filler_shape='nanosheet network', functionalization='None; radial freeze-casting alignment',
            filler_loading_vol_pct='15', filler_loading_original_value='15', filler_loading_original_unit='vol%',
            k_composite_W_mK='4.02', k_original_value='4.02', k_original_unit='W m−1 K−1',
            k_direction='through-plane',
            source_location=AB + ': "4.02 W m−1 K−1 in the through-plane direction and 3.87 W m−1 K−1 in the in-plane direction even at low BNNS loading (e.g., 15 vol%)"',
            notes='Abstract-only.'),
        row(matrix_polymer='Epoxy',
            filler_material='BNNS', filler_material_original='radially aligned BNNS lamellae (radial freeze-casting)',
            filler_shape='nanosheet network', functionalization='None; radial freeze-casting alignment',
            filler_loading_vol_pct='15', filler_loading_original_value='15', filler_loading_original_unit='vol%',
            k_composite_W_mK='3.87', k_original_value='3.87', k_original_unit='W m−1 K−1',
            k_direction='in-plane',
            source_location=AB + ': (same sentence as through-plane value)',
            notes='Abstract-only; in-plane direction.'),
    ])

# ---- P083: 10.1016/j.compositesb.2020.107855 ----
add('P083', '10.1016/j.compositesb.2020.107855',
    'Epoxy composite with significantly improved thermal conductivity by constructing a vertically aligned three-dimensional SiC nanowires/functionalized BNNS framework',
    2020, [row(
        matrix_polymer='Epoxy',
        filler_material='BNNS/SiC hybrid', filler_material_original='SiCw/f-BNNS (silicon carbide nanowires + functionalized BNNS vertical framework)',
        filler_shape='hybrid network', functionalization='BNNS surface modification (f-BNNS)',
        filler_loading_vol_pct='21.9', filler_loading_original_value='21.9', filler_loading_original_unit='vol%',
        k_composite_W_mK='4.22', k_original_value='4.22', k_original_unit='W/mK',
        k_direction='through-plane',
        source_location=AB + ': "the maximum thermal conductivity reached 4.22 W/mK at a low hybrid filler loading of 21.9 vol%, increased by 1658% in comparison to that of pure epoxy"',
        notes='Abstract-only; hybrid SiC nanowires + BNNS (both ceramics).'),
    ])

# ---- P084: 10.1177/09540083211046456 ----
add('P084', '10.1177/09540083211046456',
    'Novel layered boron nitride nanosheets/cellulose nanofibers/epoxy composite with high thermal conductivity',
    2021, [row(
        matrix_polymer='Epoxy',
        filler_material='BNNS', filler_material_original='BNNS connected with modified cellulose nanofibers (CNF), bidirectional freezing layered skeleton',
        filler_shape='nanosheet network', functionalization='CNF linkage; bidirectional freezing orientation',
        filler_loading_vol_pct='4.3', filler_loading_original_value='4.3', filler_loading_original_unit='vol%',
        k_composite_W_mK='1.43', k_original_value='1.43', k_original_unit='W/mK',
        k_direction='through-plane',
        source_location=AB + ': "thermal conductivity up to 1.43 W/mK in through-plane when filler content is 4.3 vol%"',
        notes='Abstract-only.'),
    ])

# ---- P085: 10.1177/09673911221110143 ----
add('P085', '10.1177/09673911221110143',
    'Improved thermal conductivity of epoxy composites via linked boron nitride nanosheets with in-situ generated silver',
    2022, [row(
        matrix_polymer='Epoxy resin',
        filler_material='BNNS', filler_material_original='BNNSs only (baseline in same paper; silver-linked hybrid excluded as metal-containing)',
        filler_shape='nanosheet', functionalization='None (baseline)',
        filler_loading_vol_pct='20', filler_loading_original_value='20', filler_loading_original_unit='vol%',
        k_composite_W_mK='1.26', k_original_value='1.26', k_original_unit='W/mK',
        source_location=AB + ': "The thermal conductivity increased from 1.26 W/mK for the composites only with BNNSs to 2.35 W/mK for the composites with BNNS/[Ag (2E4MI)2Ac] hybrids at 20 vol% BNNSs content."',
        notes='Abstract-only. Silver-bridged hybrid value (2.35 W/mK) NOT extracted: silver is a metal, outside ceramic-filler scope.'),
    ])

# ---- P086: 10.1016/j.cej.2018.04.196 ----
add('P086', '10.1016/j.cej.2018.04.196',
    'Melamine foam-supported 3D interconnected boron nitride nanosheets network encapsulated in epoxy to achieve significantly enhanced thermal conductivity',
    2018, [row(
        matrix_polymer='Epoxy resin',
        filler_material='BNNS', filler_material_original='MF@BNNS (BNNS-wrapped melamine foam scaffold, layer-by-layer assembly)',
        filler_shape='nanosheet network', functionalization='L-B-L assembly on melamine foam',
        filler_loading_vol_pct='1.1', filler_loading_original_value='~1.1', filler_loading_original_unit='vol%',
        k_composite_W_mK='0.6', k_original_value='0.6', k_original_unit='W m−1 K−1',
        source_location=AB + ': "a relatively high thermal conductivity of 0.6 W m−1 K−1 was achieved at an ultralow BNNS loading of ~1.1 vol%, which is equivalent to a thermal conductivity enhancement of 233% compared to epoxy resin."',
        notes='Abstract-only; loading approximate (~1.1 vol%).'),
    ])

# ---- P087: 10.1002/pc.28316 ----
add('P087', '10.1002/pc.28316',
    'Hyperbranched boron nitride structure-based epoxy composite: Simultaneous enhancement of mechanical properties and thermal conductivity',
    2023, [row(
        matrix_polymer='Epoxy resin (EP)',
        filler_material='h-BN', filler_material_original='HBP-BN (hyperbranched polymer grafted BN)',
        filler_shape='particle', functionalization='Hyperbranched polymer grafting',
        filler_loading_wt_pct='40', filler_loading_original_value='40', filler_loading_original_unit='wt%',
        k_composite_W_mK='1.1627', k_original_value='1.1627', k_original_unit='W·m−1·K−1',
        source_location=AB + ': "the composite demonstrated a remarkable 430% improvement in thermal conductivity, reaching 1.1627 W·m−1·K−1, when the HBP-BN content reached 40 wt%"',
        notes='Abstract-only. Temperature NOT specified for the TC value; paper also reports cryogenic (77 K) properties -> treat as likely RT but flag.'),
    ])

# ---- P088: 10.1002/pc.27985 ----
add('P088', '10.1002/pc.27985',
    'Boron nitride nanosheet @ quantum-sized diamond nanocrystal complex/epoxy nanocomposites with enhanced thermal conductivity',
    2021, [
        row(matrix_polymer='Epoxy',
            filler_material='BNNS/diamond hybrid', filler_material_original='BA@DN-2 (BNNS with quantum-sized diamond nanocrystals, dopamine self-assembly)',
            filler_shape='hybrid', functionalization='Acid hydroxylation + dopamine copolymerization self-assembly',
            filler_loading_wt_pct='5', filler_loading_original_value='5', filler_loading_original_unit='wt%',
            k_composite_W_mK='0.56', k_original_value='0.56', k_original_unit='W/m K',
            k_direction='through-plane',
            source_location=AB + ': "the through-plane and in-plane thermal conductivity of epoxy composite with 5% BA@DN-2 reaches to 0.56 and 3.824 W/m K, respectively."',
            notes='Abstract-only; hybrid BNNS + nanodiamond (carbon core, BNNS matrix-phase).'),
        row(matrix_polymer='Epoxy',
            filler_material='BNNS/diamond hybrid', filler_material_original='BA@DN-2 (BNNS with quantum-sized diamond nanocrystals, dopamine self-assembly)',
            filler_shape='hybrid', functionalization='Acid hydroxylation + dopamine copolymerization self-assembly',
            filler_loading_wt_pct='5', filler_loading_original_value='5', filler_loading_original_unit='wt%',
            k_composite_W_mK='3.824', k_original_value='3.824', k_original_unit='W/m K',
            k_direction='in-plane',
            source_location=AB + ': (same sentence as through-plane value)',
            notes='Abstract-only; strong anisotropy (3.824 in-plane vs 0.56 through-plane).'),
    ])

# ---- P089: 10.1016/j.jcomc.2020.100087 ----
add('P089', '10.1016/j.jcomc.2020.100087',
    'Filler surface adsorption of mesogenic epoxy for LC epoxy/MgO composites with high thermal conductivity',
    2020, [
        row(matrix_polymer='Liquid crystalline (LC) epoxy matrix',
            filler_material='MgO', filler_material_original='MgO treated with amino-silane coupling agent, with mesogenic epoxy adsorbed on surface',
            filler_shape='particle', functionalization='Amino-silane + mesogenic epoxy adsorption',
            filler_loading_vol_pct='44', filler_loading_original_value='44-45', filler_loading_original_unit='vol%',
            k_composite_W_mK='3.16', k_original_value='3.16', k_original_unit='W/(m∙K)',
            source_location=AB + ': "The thermal conductivity of the obtained composite (3.16 W/(m∙K)) was remarkably higher than that of the nonadsorbed MgO system (1.93 W/(m∙K)) at almost the same content of 44-45 vol%."',
            notes='Abstract-only; mesogenic-epoxy-adsorbed MgO system.'),
        row(matrix_polymer='Liquid crystalline (LC) epoxy matrix',
            filler_material='MgO', filler_material_original='MgO (amino-silane treated, NO mesogenic epoxy adsorption - control)',
            filler_shape='particle', functionalization='Amino-silane only',
            filler_loading_vol_pct='44', filler_loading_original_value='44-45', filler_loading_original_unit='vol%',
            k_composite_W_mK='1.93', k_original_value='1.93', k_original_unit='W/(m∙K)',
            source_location=AB + ': (same sentence as 3.16 value; control system)',
            notes='Abstract-only; control (nonadsorbed) system.'),
    ])

# ---- P090: 10.1063/1.5121349 ----
add('P090', '10.1063/1.5121349',
    'Effect of frequency of microsecond pulsed electric field on orientation of boron nitride nanosheets and thermal conductivity of epoxy composites',
    2018, [row(
        matrix_polymer='Epoxy',
        filler_material='BNNS', filler_material_original='BN nanosheets oriented by microsecond pulsed electric field (100 Hz, 11.76 kV/mm)',
        filler_shape='nanosheet', functionalization='None; electric-field orientation during cure',
        filler_alignment='Electric-field aligned (100 Hz pulsed field)',
        filler_loading_wt_pct='10', filler_loading_original_value='10', filler_loading_original_unit='wt%',
        k_composite_W_mK='0.588', k_original_value='0.588', k_original_unit='W/mK',
        source_location=AB + ': "The thermal conductivity of composites containing 10 wt.% BN nanosheets prepared under 100 Hz was 0.588 W/mK, which was more than twice that of composites without an applied electric field."',
        notes='Abstract-only; bulk composites 1.7 mm thick.'),
    ])

# ---- P091: 10.1080/15440478.2021.1966568 ----
add('P091', '10.1080/15440478.2021.1966568',
    'Thermal Conductivity of Boron Nitride/Banana Fiber Reinforced Epoxy Hybrid Composites',
    2021, [row(
        matrix_polymer='Environment-friendly epoxy',
        filler_material='h-BN', filler_material_original='BN (5 um) + banana fiber (BF) hybrid',
        filler_shape='particle', functionalization='None stated',
        filler_loading_wt_pct='5', filler_loading_original_value='5', filler_loading_original_unit='wt%',
        k_composite_W_mK='1.06741', k_original_value='1.06741', k_original_unit='W/m-K',
        source_location=AB + ': "Thermal conductivity of 1.06741 W/m-K is obtained for optimum combination of 5 wt.% of BN with particle size of 5 um and 1.2 wt.% of BF."',
        notes='Abstract-only; RSM/Box-Behnken optimized composition (BN 5 wt% + banana fiber 1.2 wt%).'),
    ])

# ---- P092: 10.1002/smll.75841 ----
add('P092', '10.1002/smll.75841',
    'Interfacial Engineering of Graphene-Derived Shells on Spherical Boron Nitride Fillers for Thermally Conductive Composites',
    2025, [row(
        matrix_polymer='Epoxy matrix',
        filler_material='BN/graphene hybrid', filler_material_original='GO-BN + prGO-BN (graphene oxide / partially reduced GO coated spherical BN, hybrid mixture)',
        filler_shape='hybrid', functionalization='GO and prGO coatings on spherical BN',
        filler_loading_wt_pct='60', filler_loading_original_value='60', filler_loading_original_unit='wt%',
        k_composite_W_mK='6.25', k_original_value='6.25', k_original_unit='W m-1 K-1',
        source_location=AB + ': "The optimized GO-BN/prGO-BN hybrid composite simultaneously achieves a thermal conductivity of 6.25 W m-1 K-1 and a volume resistivity of 1.3 × 10^12 Ω cm at 60 wt.% total filler loading"',
        notes='Abstract-only; spherical BN cores with carbon (GO/prGO) shells - hybrid flagged.'),
    ])

# ---- P093: 10.1002/pc.70149 ----
add('P093', '10.1002/pc.70149',
    'Fabrication and Thermal Conductivity Optimization of Epoxy Composites With Multidimensional Hybrid Fillers (BN@PDA/MBE)',
    2025, [row(
        matrix_polymer='Biphenyl type epoxy (MBE)',
        curing_agent="4,4'-diaminodiphenyl sulfone",
        filler_material='h-BN', filler_material_original='BN@PDA (polydopamine-coated boron nitride)',
        filler_shape='particle', functionalization='Polydopamine coating',
        filler_loading_wt_pct='20', filler_loading_original_value='20', filler_loading_original_unit='wt%',
        k_composite_W_mK='0.441', k_original_value='0.441', k_original_unit='W/(m*K)',
        source_location=AB + ': "the 20 wt% BN@PDA/MBE composite achieved optimal thermal conductivity [0.441 W/(m·K)]"',
        notes='Abstract-only. CuNW-containing hybrid (0.461 W/(m·K)) NOT extracted: copper is a metal.'),
    ])


total = 0
for cid, meta, rows in PAPERS:
    n, p = append_rows(meta, rows, dict(
        candidate_id=cid, doi=meta['doi'], paper_title=meta['paper_title'],
        date_processed='2026-10-14',
        access_result='Abstract via Semantic Scholar API (full text blocked/unreachable); Phase 3C abstract harvest',
        files_inspected='work/phase3c_abstract_hits.json (abstract text); no local fulltext',
        tables_inspected='none (abstract only)',
        figures_inspected='none (abstract only)',
        candidate_measurements=len(rows), unit_conversions='as printed unit mapped to W/(m K)',
        duplicate_checks='DOI had zero rows before this run',
        qc_findings='Abstract-only extraction; confidence=Medium; method/matrix details incomplete where not in abstract'))
    total += n
    print(cid, meta['doi'], n, 'rejected', len(p))
print('PHASE3C TOTAL ROWS:', total, 'from', len(PAPERS), 'papers')
