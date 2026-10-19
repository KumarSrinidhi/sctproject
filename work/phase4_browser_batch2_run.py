import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase4_browser_save import save
# Full text for 10.1007/s10854-024-13657-3 extracted via browser (open access Springer)
text = r'''Functionalization of boron nitride with poly(catechol-polyamine) and bis(gamma-triethoxysilylpropyl)tetrasulfide for preparing epoxy nanocomposites with enhanced thermal conductivity
Journal of Materials Science: Materials in Electronics 35, 1906 (2024)
Open access. Published: 14 October 2024.
Authors: Zijian Wu, Changjie Yang, Shunying Gao, Junguo Gao, Abdulraheem SA Almalki, Ahmed M. Fallatah, Juanna Ren, Mohamed M. Ibrahim, Ning Guo, Wei Zhao, Ling Weng, Zhanhu Guo, Zeinhom M. El-Bahy
DOI: 10.1007/s10854-024-13657-3

Abstract
Hexagonal boron nitride (hBN) has garnered significant interest as inorganic thermally conductive material in electronic packaging due to its high-efficiency thermal management capability and electrical insulation properties. However, the relatively inert chemical environment of the BN surface hinders phonon transfer at the interface. Additionally, the high content of inorganic components in the matrix leads to the deterioration of the composite's mechanical properties. In this research, h-BN surface is modified using poly(catechol-polyamine) (PCPA) and bis(gamma-triethoxysilylpropyl)tetrasulphide (Si69) (denoted as BN-PCPA-Si69). The noncovalent PCPA modification protects the endothermic properties of BN, Si69 provides covalent bonding between thermally conductive fillers and bisphenol A-type epoxy resin (Ep), and the interfacial compatibility between BN and epoxy resin is improved. The heat conductivity of final BN/Ep composite achieved 0.817 W/(m*K) containing 30 wt% BN. Correspondingly, the heat conductivity of the composite (mBN/Ep) achieved 0.881 W/(m*K) containing 30 wt% BN-PCPA-Si69. Compared to pure epoxy resin (0.200 W/(m*K)), the thermal conductivity (TC) of the mBN/Ep composite increased by 364% while maintaining good electrical insulation properties.

2 Experimental
2.1 Raw materials: Hexagonal BN (10 um) sourced from Hebei Metallurgical Powder Research Institute. Epoxy Resin (CYD-128, bisphenol A-type) from China Petroleum & Chemical Corp. Curing agent methyl tetrahydrophthalic anhydride.

2.3 Preparation: Boron nitride (10, 20 and 30 wt%) dispersed in anhydrous ethanol by ultrasonication, epoxy resin introduced, stirred at 60 C, anhydride curing agent, 2,4,6-tris(dimethylaminomethyl)phenol accelerator, ratio epoxy:hardener:accelerator = 100:81:1. Degassed and cured at 60 C then staged 80/120/150 C, 1 h each. Modified BN/Ep composites same procedure.

2.4 Characterizations: TC measured by NETZSCH LFA447 (laser flash) at room temperature.

3 Results
The heat conduction of the BN/Ep reaches 0.817 W/(mK) at BN content of 30 wt%, and that of mBN/Ep at the same content reaches 0.881 W/(mK). In comparison to pure epoxy resin (0.200 W/(m*K)), the TC of the mBN/Ep composite increased by 364%.
Conclusion section: TC of mBN30/Ep composites reaches 0.879 W/m*K.
BN filler: hexagonal, 10 um average particle size.
'''
save('10.1007/s10854-024-13657-3', text)
