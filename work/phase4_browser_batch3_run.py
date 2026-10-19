import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase4_browser_save import save
# 10.1088/1361-6463/ae6b9b — IOP blocked, abstract only (4933 chars), no captcha marker but paywalled short abstract
text = '''Interface engineering of AlN via phosphoric acid modification for enhanced thermal conduction, electrical insulation, and mechanical properties of epoxy composites
Sidi Fan, Jiarui Zhang, Peisen Hao, Xin Zhao, Yaping Cui, Wenqi Zhang
J. Phys. D: Appl. Phys. 59 205502 (2026)
DOI: 10.1088/1361-6463/ae6b9b
Publisher: IOP Publishing. Published 22 May 2026. © 2026 IOP Publishing Ltd. All rights reserved.
Abstract (publisher webpage, full text paywalled behind IOP):
Epoxy resin (EP), widely employed as an insulating material in electrical and electronic devices, faces application challenges arising from its insufficient thermal conductivity. In this work, we report a phosphoric acid modification strategy for aluminum nitride (P-AlN) fillers to resolve interfacial compatibility issues at high loadings, realizing synergistic enhancement of thermal conductivity, electrical insulation, and mechanical properties in epoxy composites. The results demonstrate that at an optimal P-AlN loading of 35 wt%, the composite exhibits a thermal conductivity of 0.41 W/mK, representing a 78.3% improvement over the pristine. [abstract truncated at page extract; further sentence on surface flashover not captured in browser innerText extract before paywall]
'''
save('10.1088/1361-6463/ae6b9b', text)
