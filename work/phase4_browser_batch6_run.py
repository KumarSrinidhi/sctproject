import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase4_browser_save import save
text = '''Sugar-template method to construct a boron nitride filler network to enhance the thermal conductivity of epoxy composites
Yifan Wang, Zhiqiang Yu
Journal of Applied Polymer Science Volume 141, Issue 27 e55612
First published: 24 April 2024
DOI: 10.1002/app.55612
Publisher: Wiley. Abstract only, full text paywalled.

Abstract
In this work, a technique for constructing a three-dimensional (3D) skeleton of hexagonal boron nitride (h-BN) using sugar as the fulcrum and preparing composites by embedding in the epoxy (EP) in a vacuum environment is proposed. The study of thermal conductivity (TC) in polymer composites is conducted through a blend of techniques: laser flashing, theoretical modeling, and finite element simulation. The h-BN skeleton exhibits a honeycomb structure through the scanning electron microscopy findings. Further investigation using finite element simulation demonstrates that conductive networks are formed by the h-BN skeleton within the composites, leading to a notable enhancement in TC. Specifically, the composite for h-BN/EP reaches a TC of 2.25 W/mK when composed of 52 vol% h-BN. A dielectric loss of 0.008 for the composite with the same h-BN loading shows a considerable improvement. The compressive yield strength of the 3D h-BN/EP composites reached 312 MPa at 5 vol% h-BN loading.
'''
save('10.1002/app.55612', text)
