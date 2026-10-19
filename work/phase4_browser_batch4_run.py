import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase4_browser_save import save
text = '''Thermal Conductive, Dielectric, and Viscosity Properties of Multidimensional Hexagonal Boron Nitride/Aluminum Modified Epoxy Resin Composites
Yu Feng, Jian Wang, Zhe Zhang, Wenchao Zhang, Jun Deng, Haibin Zhou, Zhicheng Xie, Yanjie Cui, Dong Yue, Yuanhang Yao
ChemistrySelect Volume 11, Issue 12 e07155
First published: 19 March 2026
DOI: 10.1002/slct.202507155
Publisher: Wiley (ChemistrySelect). Abstract only, full text paywalled.

ABSTRACT
Epoxy resin (EP) is widely used in electronic devices and dry-type power equipment due to its excellent insulation and thermal stability properties. However, lower thermal conductivity limits heat dissipation and the capacity improvement of equipment. Adding high thermal conductive fillers to increase thermal conductivity often increases its viscosity, which restricts the processability. In this work, multidimensional thermal conductive fillers were proposed to construct an efficient thermal conductivity network to increase the thermal conductivity of EP, and benzyl glycidyl ether (BGE) was added to reduce viscosity while ensuring other properties. The results showed that when the content of h-BN/Al2O3 was 20 wt%, the thermal conductivity reached 0.827 W/(m*K), which was 359.44% higher than that of pure EP. When the usage of BGE was 3 wt%, the viscosity of 20 wt% h-BN/Al2O3/EP suspension decreased from 13677 to 5301 mP*s, while its thermal conductivity still maintained at 0.796 W/(m*K). Zero-dimensional spherical Al2O3 was filled between two-dimensional h-BN, promoting the formation of a thermal conductivity network in composites, and this network was not severely damaged under the action of BGE. The high thermal conductivity and low viscosity EP composites will provide references for the development of insulation materials for electronic devices and dry-type power equipment.
'''
save('10.1002/slct.202507155', text)
