# Effective-medium and analytical models for k of BN-, BNNS- and AlN-filled epoxy (and other polymer) composites

Conventions used throughout these notes (to avoid the many symbol clashes between sources):
k_m = matrix conductivity, k_f (or k_p) = filler conductivity, φ = filler VOLUME fraction (0–1), k = effective composite conductivity, R_K = filler–matrix interfacial (Kapitza / thermal boundary) resistance in m²K/W, h_c = 1/R_K, a = sphere radius, a1 = a2 = in-plane semi-axis of a spheroid, a3 = semi-axis along the symmetry axis (for an h-BN platelet a3 = half the thickness t, a1 = half the diameter D), p = a3/a1 (= t/D; p < 1 oblate/platelet, p > 1 prolate/needle), a_K = R_K·k_m (Kapitza radius).

---

## 1. Model equations, parameters, assumptions, validity (Wiener, HS, Maxwell, HJ, Bruggeman/DEM/Every, Lewis–Nielsen, Agari–Uno, Nan 1997, Cheng–Vachon, Russell, percolation/Foygel, newer models)

### Takeaway
For BN/epoxy the workhorse physics model is Nan et al. 1997 (spheroids + orientation ⟨cos²θ⟩ + Kapitza resistance, with h-BN's in-plane and through-plane k inserted separately). Lewis–Nielsen is the most-used semi-empirical fit, and Foygel-type power laws are used above a ~20–25 vol% threshold. Maxwell/HJ-type models are dilute-limit models and badly underpredict platelet composites at moderate and high φ. Every equation below can be coded directly; the ambiguities in each are flagged where they occur.

### Cited Findings

#### 1.1 Wiener (parallel/series) bounds
- Rule of mixtures (parallel) k = (1 − φ)k_m + φk_f and inverse rule of mixtures (series) 1/k = (1 − φ)/k_m + φ/k_f. These are the upper and lower bounds. Lewis–Nielsen tends to the parallel form as A → ∞ and to the series form as A → 0. — [Kargar et al., arXiv 1807.03698 (UCR, 2018)](https://arxiv.org/pdf/1807.03698)
- Sarikhani et al. compare their percolation equation against the rule of mixtures, inverse rule of mixtures, Maxwell, Hashin–Shtrikman, Bruggeman asymmetric, Bruggeman symmetric and McLachlan GEM. Their measured MWCNT/PP data fall between the Hashin–Shtrikman bounds. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)

#### 1.2 Maxwell / Maxwell–Garnett / Maxwell–Eucken (spheres, dilute, no R_K)
- k/k_m = [k_f + 2k_m + 2φ(k_f − k_m)] / [k_f + 2k_m − φ(k_f − k_m)]. It assumes non-interacting spheres. Pietrak & Wiśniewski say it is valid only at low φ (under about 25%). Eucken extended it to several filler phases, and Burger and Hamilton–Crosser added particle shape. — [Pietrak & Wiśniewski, J. Power Technol. 95(1) 2015 14–24](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Sarikhani et al. say the Maxwell model applies only in the dilute limit (≲10 vol%), and that its result does not depend on sphere diameter. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- Rayleigh's correction for spheres on a simple-cubic lattice adds a φ^(10/3) term with coefficient 1.569. Its results are very close to Maxwell's, and both are "far from reality" at higher φ. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)

#### 1.3 Hasselman–Johnson (1987): Maxwell with interfacial barrier conductance h_c and particle radius a
- Sphere form, as printed in the review and checked below:
  k = k_m · [2φ(k_f/k_m − k_f/(a h_c) − 1) + k_f/k_m + 2k_f/(a h_c) + 2] / [φ(1 − k_f/k_m + k_f/(a h_c)) + k_f/k_m + 2k_f/(a h_c) + 2].
  The paper also gives a cylinder form (Rayleigh-type, cylinders ⊥ heat flow) and a flat-plate form (plates ⊥ heat flow). The key novelty is that k depends on particle size through a·h_c. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637); original: [Hasselman & Johnson, J. Compos. Mater. 21(6) 508 (1987), DOI 10.1177/002199838702100602](https://www.citedrive.com/en/discovery/effective-thermal-conductivity-of-composites-with-interfacial-thermal-barrier-resistance)
- Tavangar et al. found that the Maxwell-based Hasselman–Johnson model fails above an effective phase contrast of about 4. In contrast, a DEM (Bruggeman-type) expression with R_int matched experiments over the whole tested contrast range (2–8). They advise caution with Maxwell-based schemes when the phase contrast is high. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- The Biot-like size parameter (Devpura et al.) is Bi = R_int·k_m/(particle size). The review's eq. 16 appears to use 2a in the denominator; verify against the original. Bi > 1 makes the composite k fall below k_m even when k_f/k_m = 1000. A higher Bi also raises the filler fraction needed to reach percolation. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Sarikhani et al. call the spherical-filler model with interfacial resistance the "Hasselman–Johnson–Benveniste (HJB)" model. They call the ellipsoidal model without R_K the "Fricke / Hatta–Taya" model, and say Nan's model contains both. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)

#### 1.4 Bruggeman / differential effective medium (DEM) and Every et al. (1992)
- Among the classical effective-medium theories, the Bruggeman (DEM) scheme "is considered the most accurate for high filler volume fractions". Bruggeman-type approximations handle high φ better than Maxwell–Eucken types, although the Maxwell types are used more because they are simpler. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Every, Tzou, Hasselman & Raj (Acta Metall. Mater. 40 (1992) 123), asymmetric Bruggeman with Kapitza resistance:
  (1 − φ)³ = (k_m/k)^((1+2α)/(1−α)) · [(k − k_f(1−α)) / (k_m − k_f(1−α))]^(3/(1−α)), with α = a_K/a and a_K = R_int·k_m.
  For k_f ≫ k_m it reduces to k/k_m = 1/(1 − φ)^(3(1−α)/(1+2α)). For ZnS/diamond with a = 2 µm they fitted α ≈ 0.75. For smaller particles the data fell below the α → ∞ limit, which they attributed to non-spherical diamond. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Tavangar et al. DEM with R_int, as printed (eq. 11):
  (1 − φ) = [k_m^(1/3) · (k_f k R_int + a k − a k_f)] / [k^(1/3) · (k_f k_m R_int + a k_m − a k_f)]. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)

#### 1.5 Lewis–Nielsen (1970/1974)
- k/k_m = (1 + A·B·φ) / (1 − B·ψ·φ), with B = (k_f/k_m − 1)/(k_f/k_m + A) and ψ = 1 + [(1 − φ_m)/φ_m²]·φ.
  A = k_E − 1, where k_E is the generalized Einstein coefficient. A depends on filler shape and on orientation relative to the heat flow. φ_m is the maximum packing fraction. — [Kargar et al. 2018](https://arxiv.org/pdf/1807.03698); [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Tabulated A: spheres 1.5. Randomly oriented rods with L/D = 2, 4, 6, 10, 15 have A = 1.58, 2.08, 2.8, 4.93, 8.38. — [Pietrak & Wiśniewski 2015, Table 3](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637); same rod values quoted in [Kargar et al. 2018](https://arxiv.org/pdf/1807.03698). Nielsen's own report confirms that the Einstein coefficient of rigid spheres is 2.5, so A = 1.5 — [Nielsen, DTIC AD0748304](https://apps.dtic.mil/sti/pdfs/AD0748304.pdf)
- Tabulated φ_m (Nielsen, via the review's Table 2):
  - Spheres: hexagonal close / face-centred cubic 0.7405, body-centred cubic 0.60, simple cubic 0.524, random close 0.637, random loose 0.601.
  - Rods/fibres: uniaxial hexagonal close 0.907, uniaxial simple cubic 0.785, uniaxial random 0.82, three-dimensional random 0.52.
  The PDF text extraction scrambled the column alignment; this grouping follows Nielsen's standard table. — [Pietrak & Wiśniewski 2015, Table 2](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- Validity: the model was built for moderate φ (up to about 40%) and "becomes unstable" above that. In the review's Al2O3/PE comparison, the Nielsen model blew up above 40 vol% while the EMT model underpredicted. — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- The model implicitly assumes that no system-spanning filler network forms up to φ_m. Applying it to percolating systems needs caution. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- Platelets are not in Nielsen's table. For BN in alumina/BN/epoxy, one paper used k_f = 400 W/m·K with A = 10 for in-plane conduction and k_f = 2 W/m·K with A = 0.5 for through-plane. — [Polymers (MDPI) 2019, PMC6523155](https://pmc.ncbi.nlm.nih.gov/articles/PMC6523155/) (from the search-result abstract; full text was blocked by a CAPTCHA)
- Fibre orientation measured from micrographs has been converted into an orientation parameter inside the Lewis–Nielsen equations. That works when fibres dominate conduction, but k is underestimated when both phases are strongly conductive. — [Fraunhofer publica 259383](https://publica.fraunhofer.de/handle/publica/259383)

#### 1.6 Agari–Uno (log-linear / generalized geometric mean)
- Agari's model is routinely fitted to h-BN composites by extracting C1 and C2; for example, cyanate-ester/epoxy filled with h-BN — [Macromol. Res. 2018, s13233-018-6090-4](https://link.springer.com/doi/10.1007/s13233-018-6090-4). It is also used for porous 3D-AlN/epoxy — [Wang et al., Acta Mater. Compos. Sinica 2023](https://fhclxb.buaa.edu.cn/article/doi/10.13801/j.cnki.fhclxb.20220905.002).
- Kargar et al. tried Agari for graphene and h-BN/epoxy up to 45 vol%. Lewis–Nielsen gave the best fit; they could not find physically sensible geometric-mean fits. — [Kargar et al. 2018](https://arxiv.org/pdf/1807.03698)
- Sarikhani et al. tested Lichtenecker (geometric mean), Agari–Uno, Russell, Cheng–Vachon and Lewis–Nielsen on MWCNT/PP; only Lewis–Nielsen fitted relatively well. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- The exact equation is written out under Inferences: the original Agari & Uno 1986 text was not retrieved.

#### 1.7 Nan, Birringer, Clarke & Gleiter 1997 (J. Appl. Phys. 81, 6692)
- Scope: effective-medium theory for arbitrary spheroidal particles combined with Kapitza contact resistance. It recovers the earlier results as limiting cases and was validated on diamond/ZnS, diamond/cordierite and SiC/Al. — [KIT library record](https://publikationen.bibliothek.kit.edu/110042028); [DOI 10.1063/1.365209 (citedrive)](https://www.citedrive.com/en/discovery/effective-thermal-conductivity-of-particulate-composites-with-interfacial-thermal-resistance)
- Geometric (depolarization) factors, for p = t/D < 1 (platelet):
  L11 = L22 = p²/[2(p² − 1)] + p·cos⁻¹(p)/[2(1 − p²)^(3/2)], and L33 = 1 − 2L11. — [Yuan et al., IJHMT 94 (2016) 20, eqs. B.5–B.7](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf); [Danayat et al., arXiv 2201.03527, eq. 4](https://arxiv.org/pdf/2201.03527)
- For p > 1 (prolate): L11 = p²/[2(p² − 1)] − p·cosh⁻¹(p)/[2(p² − 1)^(3/2)]. — [Berne, COMSOL Conf. Grenoble 2015](https://www.comsol.com/paper/download/288771/berne_paper.pdf). Berne's extracted text labels p > 1 as "oblate", but the limits only work the other way round (see Inferences).
- Equivalent "coated-particle" conductivity along axis ii:
  K_ii^c = k_p,ii / (1 + γ·L_ii·k_p,ii/k_m), with γ = (1 + 2p)·α.
  Yuan et al. write γ = (1 + 2p)·R_b·k_m/t (t = platelet thickness, p = t/D) — [Yuan et al. 2016, eqs. B.4, B.8](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf). Berne writes the same quantity as K_i^c = K_p/[1 + (K_p R_Bd/a1)·L_i·(2 + 1/p)], with a1 the dimension perpendicular to the revolution axis — [Berne 2015](https://www.comsol.com/paper/download/288771/berne_paper.pdf).
- Anisotropic filler: insert the in-plane k_p1 into K11^c and the through-plane k_p3 into K33^c. — [Danayat et al., arXiv 2201.03527, eqs. 6–9](https://arxiv.org/pdf/2201.03527)
- β_ii = (K_ii^c − k_m) / [k_m + L_ii(K_ii^c − k_m)]. — [Yuan et al. 2016, eq. B.2](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf)
- Orientation-dependent effective conductivities:
  - K11* (transverse, x1) = k_m · [2 + φ{β11(1 − L11)(1 + ⟨cos²θ⟩) + β33(1 − L33)(1 − ⟨cos²θ⟩)}] / [2 − φ{β11L11(1 + ⟨cos²θ⟩) + β33L33(1 − ⟨cos²θ⟩)}] — [Danayat et al., eq. 3](https://arxiv.org/pdf/2201.03527) (the extracted denominator sign is garbled; "−" is the version that reduces to Maxwell, see Inferences)
  - K33* (along composite axis x3) = k_m · [1 + φ{β11(1 − L11)(1 − ⟨cos²θ⟩) + β33(1 − L33)⟨cos²θ⟩}] / [1 − φ{β11L11(1 − ⟨cos²θ⟩) + β33L33⟨cos²θ⟩}] — [Yuan et al. 2016, eq. B.1](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf)
  - θ is the angle between the composite axis X3 and the particle symmetry axis; for a platelet that axis is its normal. ⟨cos²θ⟩ = ∫ρ(θ)cos²θ sinθ dθ / ∫ρ(θ) sinθ dθ.
  - Random orientation: ⟨cos²θ⟩ = 1/3 and k* = k_m[3 + φ(2β11(1 − L11) + β33(1 − L33))] / [3 − φ(2β11L11 + β33L33)]. — [Yuan et al. 2016, eqs. B.3, B.9](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf)
- Known flaw: COMSOL simulations of a single particle in a cell agree with Nan within 2% for spheres with R_K and for ellipsoids without R_K. For ellipsoids with R_K the disagreement reaches about 100%, and it grows as p moves away from 1. Berne traces this to Nan's implicit assumptions: that the coated particle (particle plus resistive layer) is itself an ellipsoid, with the same aspect ratio as the bare particle. Berne derived a partial correction (an extra term A_i). — [Berne, COMSOL 2015](https://www.comsol.com/paper/download/288771/berne_paper.pdf). Per the poster summary in search results, Berne thought the practical consequences were "minimal" — [Berne poster](https://www.comsol.com/paper/download/288781/berne_poster.pdf)
- "Nan's simplified models" are used for very high-aspect-ratio CNTs. For MWCNT (aspect ratio about 34) Sarikhani et al. used the full ellipsoidal form and fitted R_K = 8.3×10⁻⁹ m²K/W (k_m = 0.15, k_f = 73.8 W/m·K). — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- Some BN papers use the needle (CNT) limit for platelets. Jang et al. 2025 write TC_Nan = k_m[3 + φ(β_x + β_z)]/[3 − φβ_x] with β_x = 2(K11^c − k_m)/(K11^c + k_m) and β_z = K33^c/k_m − 1, citing Nan et al. 2004 (APL 85, 3549, a CNT paper). They took R_ITR = 1×10⁻⁷ m²K/W from Li et al. 2016 instead of fitting it, used a_K = 65 nm and k_BN = 300 W/m·K, and report agreement with h-BN and BNNT data. — [Jang et al., Small Methods 9 (2025) 2500453, PMC12464805](https://pmc.ncbi.nlm.nih.gov/articles/PMC12464805)

#### 1.8 Percolation / power-law models, including Foygel
- Percolation types (Sarikhani et al.):
  - Type I, superconductor-like filler: k ∝ (φ_c − φ)^(−s), with s = 1.30 (2D) or 0.73 (3D).
  - Type II, insulating matrix: k ∝ (φ − φ_c)^t, with t = 1.30 (2D) or 2.0 (3D).
  - Thermal composites are Type III (poor conductor plus good conductor): a smeared crossover whose width scales with the conductivity ratio.
  They propose a "TAGP" closed-form equation, and say McLachlan's GEM equation overestimates k at the threshold. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- Foygel form as used for h-BN/epoxy: k = k_m + K0·[(φ − φ_c)/(1 − φ_c)]^β (rendered from their eq. 4, whose exponent was garbled in extraction), and the contact resistance R_c = 1/(K0·L·φ_c^β) in K/W, with L the filler length.
  Jang et al. used K0 = 7 W/m·K, β = 0.35, φ_c = 23 vol%, L = 3 µm and reported R_c = 1.20×10⁶ K/W. Recomputing their eq. 5 from these inputs gives about 8×10⁴ K/W, so the paper is internally inconsistent. They also built a hybrid "HTPM" = Nan + Foygel model for h-BN/BNNT. — [Jang et al. 2025, PMC12464805](https://pmc.ncbi.nlm.nih.gov/articles/PMC12464805); original: Foygel et al., Phys. Rev. B 71, 104201 (2005), as cited there
- For AlN/epoxy, Foygel/Agari fits gave filler–filler contact resistances of 2.704×10⁵ K/W for 3D-AlN networks and 4.019×10⁵ K/W for randomly dispersed AlN. That composite reached 1.00 W/m·K at 45.48 wt% (pure epoxy 0.18). — [Wang et al., Acta Mater. Compos. Sinica 2023](https://fhclxb.buaa.edu.cn/article/doi/10.13801/j.cnki.fhclxb.20220905.002)

#### 1.9 Newer models
- Ordóñez-Miranda crowding-factor model: built on differential effective-medium theory. It introduces a "crowding factor" set by an effective filler volume fraction, to capture particle interactions once interparticle spacing is about one particle size. It generalizes other EMT models and predicts high-φ composites well. Key papers:
  - Compos. Sci. Technol. 72 (2012) 853
  - Int. J. Thermophys. 31 (2010) 975 (generalized Bruggeman with an interface layer)
  - J. Appl. Phys. 114 (2013) 064306 (crowding factor)
  - Appl. Phys. Lett. 98 (2011) 233111
  — [Huang, Qian & Yang review, arXiv 1805.05561](https://arxiv.org/pdf/1805.05561)
- A full-field 2D homogenization alternative exists in the open-source package pyhom. — [pyhom on PyPI](https://pypi.org/project/pyhom/)

### Inferences
- **Verified identities (my calculation with the formulas above, script in scratchpad).**
  - The random-orientation Nan formula with p = 1 and R_K = 0 reproduces Maxwell exactly: 0.34963 vs 0.34963 W/m·K at φ = 0.2, k_m = 0.2, k_f = 300.
  - With R_K > 0 and p = 1 it equals Maxwell with k_f replaced by k_f,eff = k_f/(1 + k_f·R_K/a). The algebra shows this is exactly the Hasselman–Johnson sphere formula.
  - So one coded `nan1997(...)` function covers Maxwell, HJ (spheres), Fricke/Hatta–Taya (ellipsoids, R_K = 0) and platelet/needle limits. This is a good core for the module.
- **The sign in Nan's K11* denominator must be "2 − φ{…}".** Only the minus sign reduces to Maxwell's (3 + 2φβ)/(3 − φβ) for spheres. The "+" in the extracted Danayat text is a text-extraction artefact.
- **Kapitza-radius convention is ambiguous by a factor of 2.** Nan's α = a_K/a3 uses the SEMI-axis, so for p ≤ 1 γ = (1 + 2p)·R_K·k_m/a3 with a3 = t/2. I checked that this equals Berne's (2 + 1/p)·R_K·k_m/a1 and that at p = 1 it reproduces HJ, where a is the sphere radius. Yuan et al. 2016 instead use γ = (1 + 2p)·R_b·k_m/t with the FULL thickness, which halves the interfacial effect. An R_b fitted with Yuan's convention is therefore about 2× the Nan-consistent value. Store the convention alongside every fitted R_K.
- **p convention.** Nan, Yuan and Danayat define p = a3/a1 = t/D (p < 1 for platelets). Many BN papers instead quote "aspect ratio" = D/t > 1. The limits only work with the first form: as p → 0 (disc), L11 → πp/4 → 0 and L33 → 1; as p → ∞ (needle), L11 → 1/2 and L33 → 0. Berne's text labels "p > 1 oblate", which contradicts these limits; treat it as a labelling slip.
- **Useful platelet limits (p → 0)**, which make the role of R_K explicit:
  - K11^c ≈ k_p∥ / [1 + (π/4)·R_K·k_p∥/a1].
  - K33^c ≈ k_p⊥ / [1 + R_K·k_p⊥/a3].
  - Example (my calculation): h-BN with D = 5 µm, t = 250 nm, k_p∥ = 400, k_p⊥ = 5, R_K = 1×10⁻⁷ gives K11^c ≈ 28.6 W/m·K and K33^c ≈ 0.99 W/m·K. With R_K = 1×10⁻⁸ they are 174 and 3.55 W/m·K.
  - Interfacial resistance therefore throttles even micron platelets at the commonly quoted R_K ~ 10⁻⁷. This is consistent with Kargar's Lewis–Nielsen fits returning an "apparent" k_f of only about 16 W/m·K for h-BN.
- **Magnitudes from the model set (my calculation, k_m = 0.2 W/m·K).**
  - Random h-BN platelets as above, Nan model: k ≈ 0.60 / 1.74 / 3.75 W/m·K at φ = 0.1 / 0.3 / 0.5 for R_K = 0, and 0.54 / 1.43 / 2.82 for R_K = 1×10⁻⁷. This is the same order as measured random h-BN/epoxy (Kargar: about 24× k_m at 45 vol%).
  - Vertically aligned platelets (normals ⊥ heat flow, ⟨cos²θ⟩ = 0 in K33*), R_K = 1×10⁻⁸: k33 ≈ 0.78 / 2.42 / 5.3 at φ = 0.1 / 0.3 / 0.5.
  - Maxwell spheres with k_f = 400: only 0.27 / 0.46 / 0.69 at φ = 0.1 / 0.3 / 0.45.
  - Bruggeman symmetric: 0.29 / 1.84 / 70.6. It blows up above its built-in threshold φ_c = 1/3.
  - Lewis–Nielsen with Kargar's h-BN fit (A = 31, k_f = 16, φ_m = 0.52): 0.70 / 2.27 / 5.16.
- **Standard equations not retrieved verbatim this session.** These are written in their standard textbook forms and checked only by limits; verify against the originals before relying on them.
  - Hashin–Shtrikman, isotropic 3D with k_f > k_m:
    - Lower bound: k_HS− = k_m + φ / [1/(k_f − k_m) + (1 − φ)/(3k_m)] (identical to Maxwell).
    - Upper bound: k_HS+ = k_f + (1 − φ) / [1/(k_m − k_f) + φ/(3k_f)].
    - Original: Hashin & Shtrikman, J. Appl. Phys. 33, 3125 (1962).
  - Bruggeman symmetric (spheres): φ(k_f − k)/(k_f + 2k) + (1 − φ)(k_m − k)/(k_m + 2k) = 0. Closed form: k = ¼{b + √(b² + 8k_f k_m)} with b = (3φ − 1)k_f + (2 − 3φ)k_m. It has a built-in percolation threshold at φ = 1/3.
  - Bruggeman asymmetric / DEM (spheres, R_K = 0): (1 − φ) = [(k_f − k)/(k_f − k_m)]·(k_m/k)^(1/3). This is the R_int → 0 limit of the Tavangar expression in §1.4. Solve for k numerically, e.g. with `scipy.optimize.brentq` on [k_m, k_f].
  - Agari–Uno (1986): log k = φ·C2·log k_f + (1 − φ)·log(C1·k_m).
    - C1 (around 1) captures the filler's effect on polymer crystallinity or crystal size.
    - C2 (0–1) is the "ease of forming conductive chains".
    - As a linear model in φ it fits log k vs φ by linear regression: slope = C2 log k_f − log(C1 k_m), intercept = log(C1 k_m).
    - Units of k inside the log matter only through C1 and C2; report the base (log10).
  - Cheng–Vachon (1969, parabolic distribution of the dispersed phase), with B = √(3φ/2) and C = −4√(2/(3φ)) (k_m continuous, k_f dispersed):
    1/k = (1 − B)/k_m + [C(k_m − k_f)(k_m + B(k_f − k_m))]^(−1/2) · ln{ [√(k_m + B(k_f − k_m)) + (B/2)√(C(k_m − k_f))] / [√(k_m + B(k_f − k_m)) − (B/2)√(C(k_m − k_f))] }.
    It is valid for k_f > k_m because C < 0, and is undefined for φ ≥ 2/3, where B > 1.
  - Russell (1935, cubes in a series–parallel network): k/k_m = [φ^(2/3) + (k_m/k_f)(1 − φ^(2/3))] / [φ^(2/3) − φ + (k_m/k_f)(1 − φ^(2/3) + φ)]. Limits check: it gives k_m at φ = 0 and k_f at φ = 1.
  - Hamilton–Crosser: k/k_m = [k_f + (n − 1)k_m − (n − 1)φ(k_m − k_f)] / [k_f + (n − 1)k_m + φ(k_m − k_f)], with n = 3/ψ_s (ψ_s = sphericity). n = 3 gives Maxwell.
  - McLachlan GEM: (1 − φ)(k_m^(1/t) − k^(1/t))/(k_m^(1/t) + A k^(1/t)) + φ(k_f^(1/t) − k^(1/t))/(k_f^(1/t) + A k^(1/t)) = 0, with A = (1 − φ_c)/φ_c.
  - Geometric mean (Lichtenecker): k = k_f^φ · k_m^(1−φ).
- **Lewis–Nielsen ψ alternatives.** Some papers use Nielsen's alternative packing function, ψφ = 1 − exp[−φ/(1 − φ/φ_m)], instead of ψ = 1 + φ(1 − φ_m)/φ_m². This is recalled from memory and not verified this session, so code both behind a flag. With B → 1, the standard ψ makes the denominator vanish at φ = φ_m, which is the source of the instability above about 40 vol%.
- **Remaining Nielsen A values (recalled from memory, not verified this session).**
  - Cubes: A = 2.
  - Aggregated spheres: A = 2.5/φ_a − 1.
  - Uniaxial fibres: A = 2L/D for heat flow parallel to the fibres and A = 0.5 for heat flow perpendicular.
  The A = 0.5 through-plane value used for BN in PMC6523155 is consistent with that last entry.

### Gaps
- I did not retrieve the original texts of Nan 1997, Hasselman–Johnson 1987, Lewis–Nielsen 1970 / Nielsen 1974, Agari–Uno 1986, Every 1992, Cheng–Vachon 1969, Russell 1935 or Hashin–Shtrikman 1962. The equations above come from secondary sources or standard forms checked by limits, as flagged.
- Exact closed forms of the Ordóñez-Miranda crowding-factor model (JAP 2013) and the Pal model (Pal, J. Reinf. Plast. Compos. 2007, also crowding-based) were not found. Both are said to fix the high-φ failure of DEM/Maxwell by replacing φ with a crowded effective fraction depending on φ_m. The exact equations need the originals.
- Sarikhani's TAGP equation (their eq. 9) was garbled in text extraction and is not reproduced.
- The full Nielsen A table (cubes, aggregates, fibres parallel/perpendicular, platelets) could not be verified: the DTIC PDF returned 403.
- Berne's corrected term A_i is not fully reproduced; the extraction cut off.

---

## 2. Typical fitted interfacial thermal resistance (BN/epoxy, AlN/epoxy) and effect of silane/PDA functionalization

### Takeaway
Values back-fitted from composite k for h-BN/epoxy fall between about 1×10⁻⁸ and 2.4×10⁻⁶ m²K/W, typically 10⁻⁸–10⁻⁷ for "good" interfaces. MD simulations of ideal hBNNS/epoxy give only about (2.4–3.6)×10⁻⁹ m²K/W. Fitted R_K for AlN/epoxy in m²K/W was not found. Surface treatments consistently lower the fitted R_K, by about 5× in one EMA study.

### Cited Findings
- **Magnetically/mechanically aligned h-BN/epoxy** (Nan-type EMA, k_m = 0.3, k_p = 390 W/m·K taken as isotropic, D = 5 µm, t = 250 nm), fitted R_b in units of 10⁻⁹ m²K/W. — [Yuan et al., IJHMT 94 (2016) 20, Table 3](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf)

  | Volume fraction | Random | Magnetic only | Mechanical + magnetic |
  |---|---|---|---|
  | 10 vol% | 360 | 145 | 11 |
  | 15 vol% | 360 | 275 | 186 |
  | 20 vol% | 360 | 317 | 232 |

  R_b falls as alignment rises, and the aligned 10 vol% sample has 74% higher k than the unaligned one. The platelets carry Fe3O4 nanoparticles, which add to R_b. The authors attribute the lower R_b for "vertical" contacts to the higher in-plane phonon velocity of h-BN, following Prasher.
- **EMA-fitted h-BN/epoxy interface:** 2.44×10⁻⁶ m²K/W for unmodified h-BN and 4.73×10⁻⁷ m²K/W after surface modification, about one fifth of the original. — [Materials Reports 2023, cldb.21110039](https://www.mater-rep.com/EN/10.11896/cldb.21110039)
- **Literature value used without fitting:** Jang et al. took R_ITR = 1×10⁻⁷ m²K/W (from Li et al., Carbon 105 (2016) 566), giving a_K = 65 nm in their epoxy, for both h-BN and BNNT. — [Jang et al. 2025, PMC12464805](https://pmc.ncbi.nlm.nih.gov/articles/PMC12464805)
- **MD, hBN nanosheets/epoxy:** ITR = (2.42–3.62)×10⁻⁹ m²K/W, smaller than graphene/epoxy, and decaying exponentially with the number of hBN layers. — [LAMMPS abstract, Yang et al. 2020](https://lammps.org/abstracts/abstract.20131.html)
- **Liquid-crystalline epoxy on h-BN:** closely packed LC epoxy molecules lower the ITR by 21–42% in simulation and 15–65% in experiment, relative to amorphous epoxy. — [Pang et al. 2025, CityU](https://scholars.cityu.edu.hk/en/publications/reducing-the-interfacial-thermal-resistance-between-liquid-crysta/)
- **Reference points for other fillers:**
  - Graphene/PMMA interface conductance corresponds to about 1.906×10⁻⁸ m²K/W.
  - Computed critical SWCNT/polymer R_c is about 2×10⁻⁷ m²K/W; above it, k falls with loading.
  — [Huang, Qian & Yang review, arXiv 1805.05561](https://arxiv.org/pdf/1805.05561). Graphene/polymer ITR is typically 10⁻⁸–10⁻⁷ m²K/W — [Danayat et al., arXiv 2201.03527](https://arxiv.org/pdf/2201.03527)
- **Effect of processing:** in graphene/epoxy, a Nan-fitted ITR was 82% higher for acetone-processed than for DMF-processed samples, so dispersion and processing show up directly in the fitted R_K. — [Danayat et al., arXiv 2201.03527](https://arxiv.org/pdf/2201.03527)
- **Silane on BN/epoxy:** silanes with C3 and C16 chains were grafted onto BN. HDTMS (C16)-treated BN reached 3.49 W/m·K, attributed to reduced thermal contact resistance at the interface; the longer chain gave better adhesion. — [Colloids Surf. A 2017, S0927775717300110](https://www.sciencedirect.com/science/article/abs/pii/S0927775717300110)
- **Polysilazane + APTES-coated BN/epoxy:** 11.8 W/m·K at 75 wt%. — [Appl. Surf. Sci. 2020, S0169433220318481](https://www.sciencedirect.com/science/article/abs/pii/S0169433220318481)
- **Silane on AlN and BN in epoxy:** silane treatment of AlN raised composite k by lowering filler–matrix contact resistance, reaching 11.0 W/m·K at 60 vol% AlN. — [Xu & Chung, "Increasing the thermal conductivity of BN and AlN particle epoxy-matrix composites by particle surface treatments" (Univ. at Buffalo record)](https://researchconnect.buffalo.edu/en/publications/increasing-the-thermal-conductivity-of-boron-nitride-and-aluminum/)
- **KH560 silane on AlN/epoxy:** optimum at 1 wt% KH560; 1.22 W/m·K at 60% particle loading and 0.613 W/m·K at 50 wt% whiskers. Interfacial resistance is discussed, but the abstract gives no number. — [Materials Reports 2026, 25020101](https://www.mater-rep.com/EN/Y2026/V40/I5/25020101)
- **AlN in metal matrices:** interface conductance was extracted with Hasselman–Johnson plus DEM by varying AlN particle size. It rose with the metal/AlN Debye-temperature ratio, but less than models predict. — [Kida et al., J. Appl. Phys. 2011 (EPFL)](https://infoscience.epfl.ch/record/164449?ln=en)
- **AlN/epoxy contact resistance, Foygel (filler–filler, in K/W):** 2.704×10⁵ K/W (3D network) and 4.019×10⁵ K/W (random). — [Wang et al. 2023](https://fhclxb.buaa.edu.cn/article/doi/10.13801/j.cnki.fhclxb.20220905.002)

### Inferences
- **A model-fitted R_K is an "apparent" resistance.** It absorbs everything the model leaves out: voids, agglomeration, residual solvent, magnetic-nanoparticle coatings, errors in the assumed k_p⊥, and Nan's own ellipsoid-coating error. That is why EMA-fitted values (10⁻⁸–10⁻⁶) sit 1–3 orders of magnitude above MD values (about 3×10⁻⁹).
- **Suggested fitting prior for the dataset (log-uniform):**
  - 10⁻⁹ to 10⁻⁵ m²K/W, with a typical value around 10⁻⁷ for untreated h-BN/epoxy.
  - A few ×10⁻⁸ for silane-, PDA- or otherwise functionalized BN.
  - Fitted values above 10⁻⁶ indicate poor dispersion or wrong inputs, not interface physics.
- **The resistances found for AlN/epoxy are not comparable to R_K.** The Foygel R_c (K/W) is a resistance per filler–filler contact, not per unit area, so the two must not be mixed in one column of the database.
- **The functionalization effect (×1/2 to ×1/5 in R_K) is visible only when R_K matters.** In the Nan model that requires a_K = R_K·k_m to be comparable to the platelet half-thickness a3, or to (4/π)·a1·(k_m/k_p∥), the in-plane equivalent. Because a_K = R_K·k_m (for example, 1×10⁻⁷ × 0.2 = 20 nm), thin BNNS (a few nm thick) are far more sensitive to R_K than micron h-BN platelets.

### Gaps
- No PDA-specific fitted R_K value for BN/epoxy was found. A Liu et al. MD + experiment comparison of hydroxyl, PDA and silane on h-BN/epoxy exists (surfaced in search) but was not retrieved.
- No fitted AlN/epoxy R_K in m²K/W was found from the searched sources.
- The Li et al. 2016 (Carbon 105, 566) origin of the widely reused 1×10⁻⁷ value was not checked.

---

## 3. Best models for BN/epoxy at high loading (>30 vol%) and failure modes of Maxwell-type models

### Takeaway
Above about 20–25 vol%, h-BN/epoxy shows a percolation-like super-linear rise. Lewis–Nielsen (with fitted A and an apparent k_f) or a Foygel/percolation term fits much better than Maxwell, Maxwell–Garnett or Hasselman–Johnson, which systematically underpredict. Bruggeman-symmetric overpredicts past its fixed 1/3 threshold. Fitted parameters in this regime are "apparent" and not physical.

### Cited Findings
- **Kargar et al., epoxy with randomly oriented graphene or h-BN up to 45 vol%:**
  - k is roughly linear in φ up to about 30 vol% (graphene) and about 23 vol% (h-BN), then super-linear, which they read as a thermal percolation threshold.
  - Enhancement factors are about 51 (graphene, 43 vol%) and about 24 (h-BN, 45 vol%).
  - Maxwell–Garnett with TBR works for graphene below about 10 vol% but fails over the full range. The geometric-mean model could not be fitted. Lewis–Nielsen fitted best over the entire range.
  - With φ_m fixed at 0.52 (3D random), the fits gave A ≈ 31 for h-BN (61 for graphene) and apparent k_f ≈ 16 W/m·K for h-BN (37 for graphene).
  - They attribute the low apparent k_f to the cross-plane conductivity of overlapping flakes plus filler–filler TBR in the percolated network.
  — [Kargar et al. 2018, arXiv 1807.03698](https://arxiv.org/pdf/1807.03698)
- **Failures of effective-medium approximations near percolation:**
  - They are "unable to accurately predict" properties beyond the percolation threshold. They seriously underestimate k at high φ, especially the popular Hasselman–Johnson model.
  - Bruggeman types do better than Maxwell–Eucken types.
  - Lewis–Nielsen becomes unstable above 40 vol%.
  - Devpura's lattice percolation model with ITR follows the Al2O3/PE data better.
  — [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- **Linear-looking EMT curves:** classical EMT models are linear in φ only when dilute (≲10 vol%) and become non-linear at higher φ even without percolation. Caution is needed before attributing super-linearity to thermal percolation; Sarikhani et al. propose verifying percolation via universal exponents. — [Sarikhani et al., arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
- **Percolation threshold:** the h-BN network threshold is reported as 23 vol% (Jang, Foygel φ_c), consistent with Kargar. A Nan + Foygel hybrid gives 6.55–10.93 W/m·K for h-BN/BNNT at 31–50 vol%, against 5.01 W/m·K for h-BN alone at 49.45 vol%. — [Jang et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12464805)
- **Three regimes without a network:** k first rises with loading; it can then fall as aggregation reduces the filler–matrix contact area; a second rise follows once aggregates connect. Interparticle interaction matters once spacing approaches the particle size, which motivates crowding-factor models. — [Huang, Qian & Yang, arXiv 1805.05561](https://arxiv.org/pdf/1805.05561)
- **Particle form matters:** BN agglomerates gave the highest k in epoxy, contrary to the specific-surface-area expectation, so A and φ_m should differ between platelet and agglomerate fillers. — [UPC Commons, BN/epoxy particle shape study](https://upcommons.upc.edu/entities/publication/b4cb64e2-3aaf-4e4a-bbbf-6eab5d1dd555/full)

### Inferences
- **Recommended model hierarchy for the 260-row dataset.**
  1. Bounds check every row against Wiener and HS bounds. Use k_f = in-plane value for the upper bound and through-plane for the lower bound, to catch unit or vol%/wt% errors.
  2. Below about 20 vol%: Nan 1997 with anisotropic k_p, ⟨cos²θ⟩ and a fitted R_K per paper, using the filler size where it is known.
  3. At 20–60 vol%: Lewis–Nielsen with φ_m fixed by shape (0.52 for 3D-random platelets, following Kargar) and A plus apparent k_f fitted. Alternatively, a Nan(φ) + K0[(φ − φ_c)/(1 − φ_c)]^β hybrid with φ_c ≈ 0.20–0.25.
  4. Compare by AIC/BIC per paper, because Lewis–Nielsen and Foygel have 2–3 free parameters against 1 for Nan.
- **Lewis–Nielsen degeneracy.** A and φ_m (and k_f) are highly correlated when fitted together; a forum note even reports k rising as φ_m is lowered, which is counter-intuitive — [physicsforums thread](https://physicsforums.com/members/diomarte.352146/recent-content). Fix φ_m by shape class and fit only A (and optionally k_f).
- **Expect Maxwell / HJ / random-sphere models to underpredict the median data point (about 1 W/m·K) by 2–10×** wherever platelets are present (see the §1 magnitudes). Platelet-aware Nan or Lewis–Nielsen with large A are the only analytical options reaching measured values of about 3–10 W/m·K at 30–50 vol%.
- **Values of 20–47 W/m·K in the dataset are almost certainly in-plane measurements of aligned films or 3D networks.** They can be compared only with the aligned-orientation Nan or parallel-bound variants, never with random-orientation models.

### Gaps
- No single systematic benchmark comparing all the models on BN/epoxy data above 30 vol% was found. The comparisons are scattered, one paper at a time.
- The Ordóñez-Miranda and Pal crowding models have not been checked against BN/epoxy here.

---

## 4. wt% → vol% conversion; densities; intrinsic k of fillers

### Takeaway
Convert with φ = (w/ρ_f) / [w/ρ_f + (1 − w)/ρ_m], using filler-specific densities (h-BN about 2.1–2.28, AlN 3.26, epoxy about 1.16–1.2 g/cm³). Then use h-BN in-plane ≈ 400 (natural; up to 585 isotopically pure) and through-plane ≈ 2–5 W/m·K, and AlN ≈ 285 (measured single crystal) to 319–321 W/m·K (intrinsic). In polymer composites, fitted "apparent" filler k values are far lower, about 16–40 W/m·K.

### Cited Findings
- **Conversion used by Kargar et al.:** φ = (w/ρ_f) / [w/ρ_f + (1 − w)/ρ_m].
  - They started from ρ(epoxy) = 1.16, ρ(graphene) = 2.26 and ρ(h-BN) = 2.16 g/cm³.
  - They then measured each composite's density (mass/volume) and linearly regressed ρ_c = ρ_m + φ(ρ_f − ρ_m), iterating to self-consistent densities. For the h-BN set this gave ρ(h-BN) = 2.07 and ρ(epoxy) = 1.17 g/cm³ (the paper's sentence swaps the labels).
  — [Kargar et al. 2018, Methods](https://arxiv.org/pdf/1807.03698)
- **h-BN, natural bulk (TDTR):** in-plane 420 ± 46 W/m·K and through-plane 4.8 ± 0.6 W/m·K. First-principles values for natural h-BN are 537 and 4.1 W/m·K. — [Jiang et al., Phys. Rev. Materials 2, 064005 (2018), arXiv 1805.00564](https://arxiv.org/pdf/1805.00564)
- **h-BN, monoisotopic ¹⁰B:** in-plane up to 585 W/m·K at room temperature, about 80% above natural-abundance h-BN. — [Yuan, Pomeroy, Kuball et al. 2019 (ORNL listing)](https://www.ornl.gov/publication/modulating-thermal-conductivity-hexagonal-boron-nitride-controlled-boron-isotope). The listings disagree on the journal (Communications Physics vs Nature Materials).
- **Historical value:** the highest recorded room-temperature k of bulk h-BN was about 400 W/m·K, limited by isotope scattering. — [Lindsay & Broido, PRB 84, 155421 (2011)](https://link.aps.org/accepted/10.1103/PhysRevB.84.155421)
- **Suspended isotopically purified hBN:** in-plane conductivity above 1650 W/m·K was reported in a 2026 news release; the primary paper was not seen. — [C2N news, 2026](https://www.c2n.universite-paris-saclay.fr/en/science-society/news/actu/419)
- **Values modellers actually input for BN:**
  - 390 W/m·K, isotropic (Yuan et al. 2016).
  - 300 W/m·K for h-BN and BNNT (Jang et al. 2025).
  - 400 in-plane / 2 through-plane (PMC6523155).
  - Apparent 16 W/m·K, fitted with Lewis–Nielsen (Kargar 2018).
  — [Yuan 2016](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf); [Jang 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12464805); [PMC6523155](https://pmc.ncbi.nlm.nih.gov/articles/PMC6523155/); [Kargar 2018](https://arxiv.org/pdf/1807.03698)
- **AlN:**
  - The Ioffe database lists 285 W/m·K at 300 K as the maximum measured, on single crystals with varying oxygen content (Slack et al. 1987) — [Ioffe NSM AlN](https://www.ioffe.ru/SVA/NSM/Semicond/AlN/thermal.html).
  - 319 W/m·K is widely quoted as the theoretical intrinsic value, and polycrystalline AlN ceramics range from 17 to 285 W/m·K — [Franco Júnior & Shanafield, Cerâmica 2004](https://www.scielo.br/j/ce/a/7nmz9P3NBmRXqkzjGfJTMnL/?lang=en).
  - 321 W/m·K has been reported for high-quality MOCVD single crystal — [Wikipedia: AlN](https://en.wikipedia.com/wiki/AlN).

### Inferences
- **Multi-filler conversion:** φ_i = (w_i/ρ_i) / Σ_j (w_j/ρ_j), with the sum running over all components including the matrix.
  - Report ρ values with each converted row, because a ±0.1 g/cm³ error in ρ(h-BN) shifts φ by about ±2–3% relative.
  - Porosity makes the true φ smaller than the nominal φ. Where a paper reports measured composite density, use Kargar's regression approach.
- **Densities for the conversion table.** Only h-BN and epoxy values were sourced this session; the rest are standard handbook values to be verified before use.
  - h-BN 2.1–2.28 (2.07–2.16 in Kargar), cBN about 3.48, AlN 3.26, Al2O3 3.95–3.98, MgO 3.58.
  - Epoxy 1.1–1.2 (1.16–1.17 in Kargar), silicone about 1.0–1.1, polyimide about 1.4.
- **Recommended intrinsic-k defaults for the model module.** Expose them as parameters with sensitivity runs:
  - h-BN: k∥ = 400 (range 300–585) and k⊥ = 4.8 (range 2–30). The 30 upper value appears in some polymer papers and likely reflects polycrystalline averaging.
  - BNNS: k∥ = 400–750, depending on layer count.
  - AlN: 285 (range 150–320). The lower end applies to powders with oxygen impurities.
  - Fit R_K or apparent k_f rather than trusting these numbers.

### Gaps
- No sources were fetched this session for:
  - BNNS (monolayer or few-layer) intrinsic k (a value of about 750 W/m·K for monolayer BN is often cited, but was not verified).
  - cBN (several hundred to about 1600 W/m·K for isotope-enriched material, not verified).
  - Al2O3 (about 30–40 W/m·K) and MgO (about 30–60 W/m·K).
  - Densities of cBN, Al2O3, MgO, silicone and polyimide.
- The "through-plane up to 30 W/m·K" figure for h-BN in the brief was not found in any retrieved source; bulk measurements give about 4–5 W/m·K.

---

## 5. Handling h-BN anisotropy for random vs aligned orientation (orientation averaging, ⟨cos²θ⟩)

### Takeaway
The standard approach is Nan's spheroid EMA. The in-plane filler k goes into K11^c and the through-plane k into K33^c. Orientation enters only through ⟨cos²θ⟩ = ∫ρ cos²θ sinθ dθ / ∫ρ sinθ dθ (1/3 random; 0 or 1 for perfect alignment), which is measured from SEM angle histograms or estimated from XRD (100)/(002) peak ratios. Lewis–Nielsen users instead switch A and k_f between "in-plane" and "through-plane" values.

### Cited Findings
- **Yuan et al. 2016:**
  - θ is the angle between the composite axis X3 (the heat-flow direction in through-plane measurement) and the particle symmetry axis X3′, which for a platelet is its normal.
  - ⟨cos²θ⟩ was calculated from SEM angle-distribution histograms by discretization. Random gives 1/3.
  - XRD I(100)/I(002) intensity ratios served as an alignment indicator.
  - About 95.3% of platelets sat at more than 45° in the aligned 10 vol% sample.
  - Each composite's R_b was fitted with its own measured ⟨cos²θ⟩.
  — [Yuan et al., IJHMT 94 (2016) 20](https://tpl.hust.edu.cn/__local/7/55/ED/AF9F0ECE565E8FEE45F7F9108FF_98BC40C5_1D81F7.pdf?e=.pdf)
- **Danayat et al.:** used Nan's K11* with ⟨cos²θ⟩ = 1/3 for random graphene platelets, with separate in-plane k_p1 and through-plane k_p3 in K11^c and K33^c. — [Danayat et al., arXiv 2201.03527](https://arxiv.org/pdf/2201.03527)
- **Magnetically aligned hBN platelets:** a modified EMA for platelets accounts for geometry, orientation, φ and TBR, and the Supporting Information extracts R_b and ⟨cos²θ⟩. Platelets parallel to the heat flux gave 44.5% higher k than unaligned composites at 9.14 vol%; perpendicular platelets gave 37.9% lower. — [ACS Appl. Mater. Interfaces 7 (2015) 13000](https://pubs.acs.org/aamick/article-abstract/7/23/13000/767287/Thermal-Conductivity-of-Polymer-Based-Composites?redirectedFrom=fulltext); [ResearchGate copy](https://www.researchgate.net/publication/277082378_Thermal_Conductivity_of_Polymer-Based_Composites_with_Magnetic_Aligned_Hexagonal_Boron_Nitride_Platelets)
- **Lewis–Nielsen for anisotropic BN:** in-plane uses k_f = 400 and A = 10; through-plane uses k_f = 2 and A = 0.5. — [PMC6523155](https://pmc.ncbi.nlm.nih.gov/articles/PMC6523155/)
- **Filler cross-plane conductivity at high loading:** when flakes overlap, heat must cross between flakes through their thickness, so the filler's cross-plane conductivity (plus TBR at the overlaps) dominates. Kargar's finite-element two-flake model shows heat flow dropping sharply as k⊥ falls when the flakes touch; the effect vanishes at about 2 nm separation. — [Kargar et al. 2018](https://arxiv.org/pdf/1807.03698)

### Inferences
- **Mapping dataset alignment labels onto ⟨cos²θ⟩ in the K33* formula** (x3 = measurement direction, θ measured from the platelet normal):
  - Random: ⟨cos²θ⟩ = 1/3.
  - Through-plane k of in-plane-aligned films (normals ∥ x3, as from tape casting or hot pressing): ⟨cos²θ⟩ ≈ 1, giving low k.
  - Through-plane k of vertically aligned platelets (normals ⊥ x3): ⟨cos²θ⟩ ≈ 0, giving high k.
  - In-plane k: use K11* with the same ⟨cos²θ⟩.
  - Where alignment quality is unknown, fit ⟨cos²θ⟩ within [0, 1/3] or [1/3, 1] as appropriate. Better still, fix it at a literature value, because ⟨cos²θ⟩ and R_K trade off against each other.
- **Herman's orientation factor** S = (3⟨cos²θ⟩ − 1)/2 is an equivalent single-number descriptor (standard identity): S = 0 random, S = 1 for normals ∥ axis, S = −1/2 for normals ⊥ axis.
- **3D-network samples** (BN foams or aerogels infiltrated with epoxy) violate the dispersed-inclusion assumption. Model them with percolation or parallel-bound-like expressions (k ≈ φ_eff·k_network + (1 − φ)k_m), not with Nan.

### Gaps
- No standard conversion was found between the XRD I(002)/I(100) ratio and ⟨cos²θ⟩. Yuan uses the ratio only qualitatively.
- The ACS AMI 2015 Supporting Information equations were not retrieved.

---

## 6. Open-source implementations

### Takeaway
No maintained Python package implementing the thermal-composite model set (Lewis–Nielsen, Nan 1997, Agari, HJ, Foygel) was found. The project will need its own module. Some generic effective-medium and homogenization codes exist and can serve as cross-checks.

### Cited Findings
- **pyrrhenius:** includes a Bruggeman-symmetric solver, written for ionic/electrical conductivity of mixtures. — [pyrrhenius.mixing source](https://pyrrhenius.readthedocs.io/en/latest/_modules/pyrrhenius/mixing.html)
- **pyhom:** 2D full-field homogenization of effective conductivity for complex microstructures, on PyPI (2025). — [pyhom](https://pypi.org/project/pyhom/)
- **basicsums:** structural sums and effective conductivity of random 2D composites; last updated around 2019. — [basicsums](https://pypi.org/project/basicsums)
- **hashin_shtrikman_mp:** a JOSS-published Python package that uses HS bounds plus Materials Project data for inverse design; the paper notes that BurnMan also implements HS bounds. — [JOSS paper](https://www.theoj.org/joss-papers/joss.08412/10.21105.joss.08412.pdf)
- **Maxwell–Garnett / Bruggeman mixing for permittivity:** implemented in pamtra2 and rustmatrix (refractive-index mixing). The mathematics is the same because thermal and electrical conduction and permittivity problems are mathematically analogous. — [pamtra2 mixing](https://pamtra2.readthedocs.io/en/latest/autoapi/refractiveIndex/mixing/index.html); analogy: [Pietrak & Wiśniewski 2015](https://papers.itc.pw.edu.pl/index.php/JPT/article/view/463/637)
- **Commercial full-field tool:** GeoDict ConductoDict, not Python. — [GeoDict user guide](https://geodict-userguide.math2market.de/2026/conductodict.html)

### Inferences
- **Suggested module layout** (my design suggestion, based on the formulas above):
  - `bounds.py`: Wiener and HS.
  - `maxwell.py`: Maxwell, HJ, Hamilton–Crosser.
  - `nan1997.py`: depolarization factors, K_ii^c, β_ii, K11*, K33*, ⟨cos²θ⟩ helper; convention flags `a3_is_semi_axis=True` and `p = t/D`.
  - `bruggeman.py`: symmetric closed form, DEM, Every, Tavangar, solved with brentq.
  - `semi_empirical.py`: Lewis–Nielsen (two ψ options), Agari–Uno, Russell, Cheng–Vachon, geometric mean.
  - `percolation.py`: Foygel, GEM.
  - `conversions.py`: wt% → vol% and a densities table.
  - `fit.py`: scipy `least_squares` in log-k space with per-paper parameters (R_K, A, C1/C2, K0/β/φ_c), plus AIC/BIC.
- **Unit tests** should assert the limit identities verified in §1: Nan(p = 1, R_K = 0) = Maxwell, Nan(p = 1, R_K) = HJ, HS− = Maxwell, Lewis–Nielsen(A → ∞) = parallel and Lewis–Nielsen(A → 0) = series, and Every(α = 0, k_f → ∞) = (1 − φ)^(−3).

### Gaps
- GitHub was not searched directly (the web search did not surface repositories). An unpublished GitHub implementation of Lewis–Nielsen or Nan for polymer composites may exist but was not found.
