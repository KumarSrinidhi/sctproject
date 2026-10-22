# ML and Datasets for Predicting Effective Thermal Conductivity of Polymer Composites (BN / AlN / Al2O3 fillers): State of the Art, as of Oct 2026

Scope note: these notes cover (1) public datasets, (2) ML papers that predict composite k from composition and processing, (3) physics-informed and hybrid EMT+ML approaches, (4) how studies handle wt% vs vol%, direction and measurement method, (5) uncertainty quantification (UQ) for small data, and (6) best-practice and leakage lessons. Many Elsevier full texts (ScienceDirect) could not be fetched (HTTP 403), so some numbers come from abstracts or highlights only. This is flagged where it matters. **Random-split and grouped-split numbers are kept separate throughout.**

---

## 1. What published datasets exist for polymer-composite thermal conductivity (size, coverage, availability, licence)?

### Takeaway
I found no large, open, curated dataset of *filled-polymer composite* k with composition and processing metadata. Every ML paper on experimental composite k builds its own small dataset by hand from the literature (about 90 to 450 rows; 1,774 rows for one industrial set). These are usually not released as clean CSVs. The big polymer databases (PoLyInfo, Polymer Scholar, NanoMine/MaterialsMine) contain almost no usable composite-k records, or contain them only as unstructured LLM/NER extractions.

### Cited Findings
**General polymer databases**
- **PoLyInfo (NIMS):** over 18,000 homopolymers and 7,000 copolymers taken from about 20,000 papers. Only **84 homopolymers have thermal-conductivity entries** (accessed 14 Dec 2023), against more than 8,000 with Tg. PoLyInfo "is prohibited for downloading large amounts of data." — [Huang & Ju, J. Appl. Phys. 135, 171101 (2024), arXiv:2403.15887](https://arxiv.org/pdf/2403.15887)
- A 2024 data-editor review describes PoLyInfo as holding more than half a million data points and gives guidance for ML use. — [PoLyInfo (I) review, STAM Methods 2024](https://doi.org/10.1080/27660400.2024.2354649)
- **RadonPy:** to work around PoLyInfo's download restriction, Hayashi et al. picked 1,070 amorphous polymers from PoLyInfo and computed 15 properties, including TC, with all-atom MD. These are neat polymers only, not composites. — [Huang & Ju 2024](https://arxiv.org/pdf/2403.15887)
- **Wu et al. 2019 (npj Comput. Mater. 5, 66):** used PoLyInfo and transfer learning from proxy properties (Tg, Tm) to predict neat-polymer k. Three designed polymers were synthesised at 0.18 to 0.41 W/m·K. — [Nature](https://www.nature.com/articles/s41524-019-0203-2); NIMS dataset record at [MDR](https://mdr.nims.go.jp/datasets/f2b2dca6-0f86-4212-ab79-a332ce6ae4c3). A transfer-learning review reports that the best transferred model cut MAE by about 37% versus direct training, **using only 28 k training instances**. — [arXiv:2403.12982](https://arxiv.org/pdf/2403.12982)
- **Khazana / Polymer Genome (Ramprasad group):** holds DFT-computed properties such as refractive index, dielectric constant and band gap. It is not a source of experimental composite k. — [Huang & Ju 2024](https://arxiv.org/pdf/2403.15887)

**LLM / NLP-extracted data (2024–2026)**
- **Polymer Scholar (Gupta, Mahmood, Shetty, Adeboye, Ramprasad, Communications Materials 2024):**
  - Corpus: about 2.4 M full-text articles (published up to 2021); 681k polymer-related articles; over 1 M records for 24 properties of more than 106k polymers.
  - **Thermal-conductivity records:** 5,574 (GPT-3.5, full text), 10,300 (MaterialsBERT, full text) and 1,429 (MaterialsBERT, abstracts).
  - Extraction quality: F1 = 0.67 (GPT-3.5, Tg) and 0.85 (bandgap).
  - Composites are a known weak spot: MaterialsBERT "often extracted redundant values for each polymer" in blends/composites, inflating counts. GPT-3.5 handled composite compositions better but still missed fillers in complex sentences.
  - Cost: full-corpus GPT-3.5 extraction took about 1 month and about US$1,200.
  - Data can be "freely explored" at polymerscholar.org.
  - Source: [Gupta et al. 2024 PDF](https://ramprasad.mse.gatech.edu/wp-content/uploads/2025/01/s43246-024-00708-9.pdf)
- **LLM extraction for inorganic thermoelectrics (2025):** an agentic pipeline over about 10,000 articles; GPT-4.1 reached F1 = 0.91 on thermoelectric properties and 0.82 on structural fields; 27,822 temperature-resolved records, including k. Shows feasibility, but not for polymer composites. — [arXiv:2510.01235](https://arxiv.org/html/2510.01235v1)
- **BNNS synthesis (2025):** an LLM/RAG "lightly structured text database" was used for BN nanosheet exfoliation protocols. It covers synthesis guidance, not a k dataset. — [arXiv:2509.06093](https://doi.org/10.48550/arxiv.2509.06093)

**Nanocomposite-specific infrastructure**
- **NanoMine / MaterialsMine (Brinson, Schadler et al.):**
  - An XML schema and ontology for polymer nanocomposites. — [APL Materials 2018](https://doi.org/10.1063/1.5046839)
  - A 2023 case study used more than 2,000 curated experimental samples, but for ΔTg, not k. — [Macromolecules 2023](https://doi.org/10.1021/acs.macromol.2c02249)
  - **ChemProps:** a RESTful API that standardises free-text polymer names to SMILES; 100% test accuracy on 54 test names. — [J. Cheminform. 2021](https://doi.org/10.1186/s13321-021-00502-6)

**Datasets accompanying composite-k ML papers** (none confirmed as openly licensed CSVs)
- Liu et al. 2024 (Materials Today Commun. 39, 109116): a "unique dataset" of single-filler polymer composites taken from earlier experimental papers. Size and release were not visible in the abstract. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2352492824010973)
- Han et al. 2025 (Mater. Genome Eng. Adv. 3, e70027): **1,774 experimental data points**. Search snippets describe these as thermally conductive compounds from Korean manufacturers, which suggests industrial and likely proprietary data. — [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/mgea.70027)
- Carbon-filled polymer composites (J. Mater. Sci. Technol. 2026): **370 valid literature samples**. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1005030226000046)
- PCM composites, 447 literature records. — [ScienceDirect 2025](https://www.sciencedirect.com/science/article/pii/S2772826925000902)
- Epoxy–filler composites for cryogenic use, 364 samples, with features k_matrix, k_filler, vol fraction and temperature. — [Springer LNNS 2026](https://link.springer.com/chapter/10.1007/978-3-032-26376-6_5)
- Nano-enhanced PCMs, 150 measurements from 21 studies. — [Alqurashi & Khan, Sci. Rep. 2026](https://www.nature.com/articles/s41598-026-68034-3)
- Bio-composites, 93 literature samples. — [EPJ Web Conf. 2026](https://doi.org/10.1051/epjconf/202637102013)
- Mycelium composites, 331 observations from 47 studies. — [Materials & Design 2026](https://doi.org/10.1016/j.matdes.2026.116566)
- **Kaggle "Polymer Composite Properties Dataset":** 12,700 samples × 35 columns in one CSV (composition, filler properties, thermal behaviour). Its provenance is not documented in the search snippet. — [Kaggle](https://www.kaggle.com/datasets/colabsss/polymer-composite-properties-dataset)

**Simulation-generated composite datasets** (open data status mostly unclear)
- 1,024 COMSOL RVE models of multifiller composites (RF + CNN). — [ACS AMI 2025](https://doi.org/10.1021/acsami.5c21877)
- About 690,000 formulations generated with a physics-based homogenization model for hybrid liquid-metal composites. — [Adv. Funct. Mater. 2026](https://doi.org/10.1002/adfm.75719)
- RVE/FEM datasets for graphene and CNT/polymer composites (XGBoost + SHAP/LIME + UQ). — [Composite Structures 2025](https://doi.org/10.1016/j.compstruct.2025.119292)

**Filler intrinsic k (AFLOW etc.)**
- **AFLOW-AAPL** (automated anharmonic phonon / Boltzmann transport) was validated on 30 materials. — [arXiv:1611.05481](https://arxiv.org/pdf/1611.05481)
- **AFLOW AEL-AGL** (quasi-harmonic Debye) screened more than 3,000 AFLOW materials. Its high-k list is "dominated by various phases of elemental carbon, boron nitride, boron carbide and boron carbon nitride." — [arXiv:1611.05714](https://arxiv.org/pdf/1611.05714)
- Indicative handbook ranges from a vendor blog (treat with caution): h-BN 200–400 W/m·K in-plane (typical loadings 40–70 vol%); Al2O3 25–35 W/m·K. — [Patsnap blog](https://www.patsnap.com/resources/blog/articles/thermally-conductive-polymer-composites-for-power-electronics/)

### Inferences
- The project's 260-row / 95-paper set is about the same size as most published experimental composite-k sets (93–450 rows). Its 95 source papers make it unusually diverse per row (about 2.7 rows per paper), which makes grouped CV harsher but more honest.
- Polymer Scholar's roughly 5.6k GPT-3.5 k records could be a candidate source for *expanding* the dataset. They would need manual verification of filler identity, loading and units, because composite parsing is the known failure mode.
- Filler intrinsic k is best handled as a small hand-curated lookup table (h-BN in-plane vs through-plane, AlN, Al2O3, BNNS) with citations, not pulled from AFLOW. AFLOW computes ideal single-crystal lattice k, which overstates the k of real powders, defective flakes and nanosheets.
- The Kaggle 12.7k-row dataset should not be used as ground truth unless its provenance is confirmed. Its size is implausible for a hand-curated experimental set.

### Gaps
- No licence terms could be confirmed for Polymer Scholar *data* (the paper is CC BY-NC-ND 4.0), PoLyInfo (only "bulk download prohibited"), or the per-paper supplementary datasets.
- I could not confirm a public GitHub/Zenodo/Figshare CSV of experimental BN/AlN/Al2O3–epoxy k with metadata; searches returned none.
- I could not confirm whether Materials Project hosts lattice k for BN/AlN/Al2O3, or the exact AAPL compound count.
- Dataset sizes for Liu et al. 2024 and the Co-ANN BN paper could not be read (paywalled).

---

## 2. Which ML papers predict composite k from composition/processing; what features, sizes, accuracies; were splits leakage-free?

### Takeaway
Almost all published composite-k ML papers report **random-split** test metrics with R² of about 0.9 to 0.99, using tree ensembles (GBDT/XGBoost/RF) or small ANNs. The few studies that tested **leave-source-out** generalisation found collapse: R² fell from about 0.46 (random 10-fold) to about 0.05 when whole studies were held out. Filler loading dominates every SHAP or feature-importance analysis.

### Cited Findings
**Experimental / literature-data studies (random or unspecified splits)**
- **Liu et al. 2024, Materials Today Commun. 39:109116** (single-filler polymer composites, literature data):
  - Compared RF, GBDT, XGBoost and GPR; GBDT was best, with **Pearson r = 0.981** on the test set after feature selection.
  - Filler volume fraction and matrix k were the most influential inputs; "the thermal conductivity of the fillers has a relatively minor impact."
  - Introduced **topological polar surface area (TPSA)** as a descriptor that quantifies surface-modifying agents.
  - Split type not visible in the abstract.
  - Sources: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2352492824010973); citation details confirmed in [arXiv:2501.15231 refs](https://arxiv.org/pdf/2501.15231)
- **Han et al. 2025, MGEA:** XGBoost on 1,774 experimental points predicting 7 properties, including TC. "Average R² of 0.95" across properties; no per-property TC metric in the abstract. Several composition representations were tested, and product-grade information was added as a feature. Validation scheme not stated in the abstract. — [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/mgea.70027); [HEP mirror](https://journal.hep.com.cn/mgea/EN/10.1002/mgea.70027)
- **Enhanced Co-ANN for polymer/BN composites at high filler fraction (Energy and AI 2025):**
  - Design: semi-supervised co-training ANN that uses unlabeled inputs, a multi-head "physical attention" layer, and a physics-constrained loss.
  - Accuracy: **R² = 0.982, MAE = 0.045 W/m·K**, reported as better than classical models and a plain ANN.
  - Attention concentrates on filler volume fraction and interface effects.
  - Validation used six groups of samples made at different packing fractions; dataset size unknown.
  - Source: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666546825001958)
- **Carbon-filled polymer composites (JMST 2026):** 370 literature samples. SHAP showed numerical features matter more than categorical ones, and filler loading dominates. The authors screened 32,327 candidate groups, and three candidates were synthesised with measured k "fully consistent" with predictions. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1005030226000046)
- **Single-lab epoxy/glass-fiber with aerosil, Al2O3, Cr2O3 (Aviation 2024):** NN test errors of 0.2–0.5% and boosted trees 0.9–1.5%. This is single-source data, so interpolation is easy. — [Aviation 2024](https://doi.org/10.3846/aviation.2024.21472)
- **Ding et al. 2022, Chem. Eng. J. 437:135438 (h-BN/polyimide):** combined an iterative EMT model (used to infer reduced thermal boundary resistance) with an ANN predicting in-plane k versus filler content and temperature. In-plane k was 6.57 W/m·K at 30 vol% exfoliated BN, versus 3.92 for pristine h-BN/PI. — [NWPU record](https://pure.nwpu.edu.cn/en/publications/thermal-conductivity-of-polydisperse-hexagonal-bnpolyimide-compos)
- **PEG nanocomposites (229 samples):**
  - GBM with a 90/10 split: train R² = 0.9966, **test R² = 0.9158**. — [An. Acad. Bras. Ciênc. 2025](https://doi.org/10.1590/0001-3765202520241430)
  - On the same 229-sample data, RF optimised by the bat algorithm reached R² = 0.995. — [Discover Nano 2026](https://doi.org/10.1186/s11671-026-04677-5)
- **PCM composites:** ANN R² ≈ 0.97 on literature data (447 records). — [SCCA 2025](https://www.sciencedirect.com/science/article/pii/S2772826925000902)
- **Bio-composites:** 93 literature samples; RF R² = 0.885, RMSE = 0.042 on a train–test split. — [EPJ Web Conf. 2026](https://doi.org/10.1051/epjconf/202637102013)
- **CF/polyimide (Materials 2026):** two-stage CatBoost/XGBoost model. Introduced a composition-derived interface feature (carbon-filler-to-sizing-agent mass ratio). Experimental validation confirmed predicted trends. — [Materials 2026](https://doi.org/10.3390/ma19173667)

**Studies that tested cross-source generalisation**
- **Alqurashi & Khan, Sci. Rep. 2026** (nano-enhanced PCMs; **150 measurements from 21 studies**):
  - Target: log10(k_eff/k_base).
  - "Preprocessing-leakage-free" 10-fold CV: GBR **R² = 0.46 ± 0.56**, RF 0.43 ± 0.70; best RMSE 0.17 and MAE 0.10 (log units).
  - SVR and the NN had **negative CV R²** despite high training scores.
  - Loading and filler intrinsic k were the dominant descriptors.
  - **Leave-one-source-out R² ≈ 0.05.** The authors conclude the model suits "screening within represented material families but not … quantitative prediction of unseen source systems without retraining."
  - Source: [Nature Sci. Rep.](https://www.nature.com/articles/s41598-026-68034-3)
- **Mycelium biocomposites meta-dataset (331 obs / 47 studies):** RF validation for k gave RMSE = 0.014 and MAE = 0.011. The authors stress "limited cross-study predictability" and "notable" heterogeneity. — [Materials & Design 2026](https://doi.org/10.1016/j.matdes.2026.116566)

**Simulation-trained / microstructure-image models** (high accuracy, but on synthetic, in-distribution data)
- **Wei et al. 2018, IJHMT:** SVR, GPR and CNN trained on simulated microstructures all beat the Maxwell–Eucken and Bruggeman models. Reported CNN RMSE of about 1.9% versus 7.3% (Maxwell–Eucken) and 18.3% (Bruggeman). — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0017931018317423); [ResearchGate](https://www.researchgate.net/publication/329056556_Predicting_the_effective_thermal_conductivities_of_composite_materials_and_porous_media_by_machine_learning_methods)
- **Cross-section CNN study (Compos. Sci. Technol. 2019; arXiv:1904.06104):** 2D cross-section CNNs match 3D CNNs when multiple sections are used. Sections along the heat-flow direction are more informative. — [arXiv:1904.06104](https://arxiv.org/pdf/1904.06104)
- **1D oriented fillers (Energy and AI 2024):**
  - CNN on carbon fiber–epoxy reached R² = 0.924.
  - A defined "orientation degree" descriptor (O_d) was predicted by CNN with R² = 0.950; RF using O_d then predicted k with **R² = 0.954**.
  - Extended to other 1D fillers and matrices; used symbolic regression for interpretability.
  - Source: [Energy and AI](https://doi.org/10.1016/j.egyai.2024.100445)
- **Multifiller RVEs (ACS AMI 2025):** 1,024 COMSOL RVEs. Thermally-conductive-pathway descriptors improved RF/CNN accuracy; pathways "markedly enhanced TC" at low filler fraction. — [ACS AMI](https://doi.org/10.1021/acsami.5c21877)
- **Bayesian optimisation for alumina/PDMS (Compos. Sci. Technol. 2025):** optimised a 4-size Al2O3 blend (90, 20, 3, 0.6 µm) to about **6.89 W/m·K**. 3D X-ray CT showed particle connectivity and interfacial area critically influence k. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0266353825003689)
- **3D X-ray CT descriptor follow-up:** the highest k comes from "an optimized balance of high loading, moderated tortuosity, and controlled interfacial area," not maximum loading. — [PMC12716219](https://pmc.ncbi.nlm.nih.gov/articles/PMC12716219)
- **IR thermography + ML (ACS AMI 2025), a characterisation-technique angle:** more than 200 thermal images from experiments and multiphysics simulations, turned into gradient, Laplacian and extrema features, predicting cross-plane k below 5 W/m·K. RF reached **R² = 0.905, MAE = 0.169** on experimental test sets. Domain adaptation used Gaussian-perturbed simulations. — [ACS AMI](https://doi.org/10.1021/acsami.5c19562)

### Inferences
- **Realistic accuracy for the project (inference, not a published number):**
  - Random K-fold on 260 rows will probably give R² ≥ 0.85 on log10 k. Because many rows share a paper (same matrix, filler and process), this mostly measures within-paper interpolation along the loading curve.
  - Under GroupKFold or leave-one-paper-out, the closest analogue (Alqurashi & Khan: 21 sources, log-ratio target) suggests R² on the log target could drop to about 0–0.5.
  - A reasonable "good" outcome is MAE in log10 k of about 0.15–0.30 (a factor of about 1.4–2 in k), beating an EMT-only baseline and a 1-NN or "predict group mean" baseline.
  - The 2–4× degradation from random to cluster splits (Meredig, Section 6) points the same way.
- Most published R² values of 0.95–0.99 are likely **inflated by within-paper leakage**: random splits put points from the same loading series in both train and test. Rows from one paper share undisclosed factors (dispersion quality, the lab's measurement setup), so treat these numbers as upper bounds.
- Liu et al.'s finding that filler k matters little matches EMT physics. When k_filler/k_matrix ≫ 1 (e.g., BN/epoxy at about 1000×), Maxwell-type predictions saturate, so loading, shape/aspect ratio, interfaces and network formation dominate. This argues for shape/aspect and interface/functionalisation features over precise filler-k values.
- The descriptor ideas transfer to this project's free-text fields: TPSA for surface modifiers (Liu 2024), a sizing/functionalisation ratio (CF/PI 2026), orientation degree (Energy and AI 2024), and pathway/connectivity (ACS AMI 2025). Functionalisation, for example, can become a binary flag or a coarse class (silane / dopamine / covalent / none).

### Gaps
- None of the experimental composite-k papers I could access (abstracts) reported **grouped-by-paper** CV except Alqurashi & Khan (PCMs). No BN/AlN/Al2O3–epoxy paper with a leave-paper-out score was found.
- Full feature lists, dataset sizes and split details for Liu 2024, Co-ANN 2025 and Han 2025 are behind paywalls.
- I found no symbolic-regression or transfer-learning study trained on *experimental* filled-polymer k (symbolic regression appears only with simulated data).

---

## 3. Physics-informed approaches: EMT predictions as features/baselines, residual learning, monotonicity, log targets

### Takeaway
Explicit "EMT prediction as feature" or "ML on the EMT residual" work for experimental polymer composites is rare. The closest published examples are the BN Co-ANN (physics-constrained loss), Ding 2022 (iterative EMT + ANN), and simulation-trained surrogates. The strongest general evidence comes from small-data materials ML: adding a crude physics estimate as a feature helps (Zhang & Ling 2018), and monotonic GPs reduce variance at a small accuracy cost. A log or log-ratio target is used in the one study with honest grouped validation.

### Cited Findings
- **Crude-estimate-as-feature (Zhang & Ling 2018):** for small materials datasets, "incorporate the crude estimation of property in the feature space," which "increases the accuracy of prediction without the cost of higher DoF." It brought small-data models "to state-of-art levels" in three case studies, one being **lattice thermal conductivity**. — [npj Comput. Mater. 4, 25 (2018)](https://doi.org/10.1038/s41524-018-0081-z)
- **Monotonic GP (Tran et al. 2022):**
  - Tested on 3 materials datasets (1 experimental, 2 computational) and gave "a significant reduction in the posterior variance."
  - Strictly monotonic when interpolating, but "the monotonic effect starts fading away" beyond the training data.
  - Costs a small amount of accuracy versus a regular GP; most useful when "data are scarce and noisy, and monotonicity is supported by strong physical evidence."
  - Source: [J. Comput. Inf. Sci. Eng. 2022](https://doi.org/10.1115/1.4055852); [arXiv](https://arxiv.org/pdf/2209.00628)
- **Monotonic constraints in gradient boosting** are supported directly in scikit-learn (example of monotonic constraints on a GB estimator). — [scikit-learn docs](https://scikit-learn.org/1.3/_sources/auto_examples/ensemble/plot_monotonic_constraints.rst.txt)
- **Physics-guided BN composite model (Energy and AI 2025):** physics-constrained loss plus physical attention; R² = 0.982, MAE = 0.045 W/m·K. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666546825001958)
- **Iterative EMT + ANN for h-BN/PI (Ding et al. 2022):** EMT used to infer thermal boundary resistance; ANN for interpolating k over loading and temperature. — [NWPU](https://pure.nwpu.edu.cn/en/publications/thermal-conductivity-of-polydisperse-hexagonal-bnpolyimide-compos)
- **ML vs EMT baselines (Wei 2018):** on simulated data, SVR/GPR/CNN all beat Maxwell–Eucken and Bruggeman. The authors frame ML as "semi-analytical models" similar to EMT. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0017931018317423)
- **EMT model limits relevant to residual learning:**
  - **Lewis–Nielsen:** tested against 17 experimental k datasets on particulate composites; fits many of them well, but the maximum packing fraction ranges 0.32 to 1.0 depending on the system. — [Composites Part A 2008](https://www.sciencedirect.com/science/article/abs/pii/S1359835X08000389)
  - Lewis–Nielsen cannot predict the percolation threshold. — [arXiv:2209.07635](https://arxiv.org/pdf/2209.07635)
  - Lewis–Nielsen omits interfacial thermal resistance (ITR); a three-phase extension, with fitting parameters derived from a 16 nm interfacial thickness, was fitted to epoxy filled with Al2O3, AlN and MgO. — [ResearchGate](https://www.researchgate.net/publication/238594787_Three-phase_lewis-nielsen_model_for_the_thermal_conductivity_of_polymer_nanocomposites)
- **Maxwell variants:** Maxwell–Eucken fit microcomposites well and Maxwell–Garnett fit nanocomposites well in one metallic-network/polymer study. — [US patent 9045674](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9045674)
- **Log-ratio target:** the only grouped-validated study used y = log10(k_eff/k_base), a dimensionless log enhancement ratio. — [Sci. Rep. 2026](https://www.nature.com/articles/s41598-026-68034-3)
- **Physics-generated training data** is another hybrid route: about 690,000 homogenization-model formulations plus RF and Bayesian optimisation for hybrid liquid-metal composites (k ≈ 2.4 W/m·K achieved). — [Adv. Funct. Mater. 2026](https://doi.org/10.1002/adfm.75719). Similar RVE/FEM data were combined with XGBoost + SHAP/LIME + UQ. — [Compos. Struct. 2025](https://doi.org/10.1016/j.compstruct.2025.119292)

### Inferences
- **Recommended physics-informed design for 260 rows (inference):**
  1. Target y = log10(k_c) or y = log10(k_c/k_m), imputing k_m from a polymer-class default when missing. For epoxy, about 0.2 W/m·K is typical; for example, an epoxy at 0.22 W/m·K rose to 1.72 W/m·K at 80 wt% Al2O3/BN ([PMC7795928](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7795928/)).
  2. Compute EMT features per row: Maxwell–Garnett; Lewis–Nielsen with shape factor A and maximum packing φ_m set by filler-shape class; optionally Hasselman–Johnson/Nan with an assumed Kapitza radius. Use them (a) as baselines to beat, (b) as input features (Zhang & Ling style), and (c) as an offset for residual learning, y − log10(k_EMT).
  3. Impose monotone-increasing constraints on loading (vol%) in GBM (scikit-learn HistGradientBoosting, XGBoost or LightGBM all support them), or use a GP with the EMT as its mean function.
- Residual learning on the log scale keeps predictions physically plausible: correct limits at 0 vol% and monotone in loading. It also lets the ML part learn interface, alignment and processing effects, which EMT ignores. This matches the project's course theme of connecting characterisation physics with data.
- Percolation-like jumps (aligned BN, 3D BN networks, hybrids) are where all EMTs fail. Hybrid and aligned rows may need separate indicator features, or should be excluded from the EMT-residual model and reported separately.
- Caveat: monotonic constraints fade outside the training range (monotonic GP study), so they help mainly in interpolation; they do not license extrapolation to very high loadings.

### Gaps
- No peer-reviewed paper was found that does residual learning on Maxwell/Lewis–Nielsen for *experimental* polymer-composite k with grouped validation. Its benefit for this exact setting is not demonstrated in the literature.
- Hasselman–Johnson/Agari/Nan models used as ML features were not found in accessible abstracts; ITR values (Kapitza radii) for BN/epoxy would need sourcing elsewhere.

---

## 4. How do studies handle wt% vs vol%, anisotropy/direction, and measurement-method heterogeneity?

### Takeaway
Most composite-k ML papers use **volume fraction** as the key physics variable (Liu 2024; cryogenic epoxy set; Co-ANN). They rarely document how wt% was converted, how in-plane and through-plane values were separated, or how measurement method was encoded. Hot-disk vs laser-flash differences for platelet (BN) composites can reach about 50%, comparable to model error, so method and direction metadata matter.

### Cited Findings
- Filler **volume fraction** is the top-ranked feature in Liu 2024 ("filler volume fraction and matrix thermal conductivity significantly influence"). — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2352492824010973). It is also an explicit input in the cryogenic epoxy–filler set (k_matrix, k_filler, vol fraction, temperature). — [Springer 2026](https://link.springer.com/chapter/10.1007/978-3-032-26376-6_5)
- The Co-ANN BN study highlights filler volume fraction as the key design variable; attention focuses on volume fraction and interface effects. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666546825001958)
- **Anisotropy and orientation:** Energy and AI 2024 handles orientation by defining a quantitative "orientation degree" O_d descriptor. — [Energy and AI](https://doi.org/10.1016/j.egyai.2024.100445). Ding 2022 models **in-plane** k only. — [NWPU](https://pure.nwpu.edu.cn/en/publications/thermal-conductivity-of-polydisperse-hexagonal-bnpolyimide-compos)
- 2D cross-sections taken along the heat-flow direction are more informative than those perpendicular to it, because they distinguish series from parallel structures. — [CST 2019 cross-section CNN study, arXiv:1904.06104](https://arxiv.org/pdf/1904.06104)
- **Measurement-method heterogeneity:**
  - A BN-compound patent reports that through-plane hot-disk measurements on 4 mm injection-moulded plates read **about 15–20% higher than laser flash on 2 mm plates for isotropic fillers, and up to 50% higher for platelet fillers**. It also says values are "only directly comparable" under identical compounding, shaping, sampling and measurement conditions. — [US patent 10328620](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10328620)
  - Laser flash measures diffusivity, and k = α·ρ·Cp, so density and Cp errors propagate directly into k. — [same patent](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10328620)
- **Normalising per-study systematic offsets:** the log enhancement ratio log10(k_eff/k_base) removes the matrix baseline measured by the same lab and method. — [Sci. Rep. 2026](https://www.nature.com/articles/s41598-026-68034-3)
- Inconsistent testing methods and incomplete metadata are named as core barriers to cross-study polymer ML. — [Zhao, Chen, Liu, arXiv:2505.13494 (2025)](https://arxiv.org/abs/2505.13494)
- Artrith et al. checklist item 2c asks whether "instances of combining data from multiple sources [are] clearly identified, and potential issues mitigated." The text also stresses characterising "possible discrepancies between sources, and the impact of homogenization." — [Nat. Chem. 2021](https://www.coudert.name/papers/10.1038_s41557-021-00716-z.pdf)

### Inferences
- **wt% → vol%:** convert with φ_f = (w_f/ρ_f) / (w_f/ρ_f + (1 − w_f)/ρ_m). Example densities: h-BN about 2.1–2.28, AlN about 3.26, Al2O3 about 3.95, epoxy about 1.1–1.2 g/cm³. These are standard handbook values that should be cited in the project's own data dictionary; I did not source them here. Keep a flag saying vol% was derived, not reported, and ignore porosity unless it is reported. This produces one physics-consistent loading variable for all 260 rows (191 have wt%, 104 have vol%).
- **Direction:** encode k_direction as {through-plane, in-plane, isotropic/unknown} and combine with alignment and shape. Because direction is "mostly unknown," run a sensitivity analysis: (a) all rows; (b) excluding rows with known in-plane values or known alignment. In-plane values of aligned BN can exceed through-plane values by large factors and will otherwise dominate the residuals.
- **Measurement method:** encode it as a categorical feature (LFA / hot disk / steady-state, ASTM D5470 or guarded hot plate / other), and also report a stratified error breakdown. With only about 95 papers, method is partly confounded with paper, so its learned coefficient will be noisy; a per-method error table is more informative for a characterisation course.
- Using log10(k_c/k_m) when k_m is reported in the same paper (127 rows) partly cancels lab- and method-level offsets, as in Alqurashi & Khan.

### Gaps
- No controlled interlaboratory comparison (LFA vs hot disk vs steady state) on BN/epoxy composites was found in this search. The 15–50% figure is from a single patent.
- No accessible composite-k ML paper reported how it converted wt% to vol% or treated missing direction labels.

---

## 5. Uncertainty quantification for small materials datasets (GP, quantile regression, conformal, bootstrap ensembles)

### Takeaway
For about 260 rows, the defensible options are: GP regression (native predictive variance, can carry an EMT mean and monotonic constraints), bootstrap or ensemble trees **with post-hoc calibration**, and (split or cross-) conformal intervals computed over **paper-grouped** folds. Uncalibrated ensemble spread is known to be inaccurate, and conformal guarantees weaken when the calibration set is small.

### Cited Findings
- **Calibrated bootstrap (Palmer et al. 2022):** "the direct bootstrap ensemble standard deviation is not an accurate estimate of uncertainty but … it can be simply calibrated to dramatically improve its accuracy." Shown on synthetic data and several materials datasets. — [npj Comput. Mater. 8, 115 (2022)](https://doi.org/10.1038/s41524-022-00794-8)
- **UQ evaluation metrics (Tran et al. 2020):** proposes figures and metrics for accuracy, **calibration and sharpness**. In their case study, a CNN-feature + GP model gave the best uncertainty estimates. — [Mach. Learn.: Sci. Technol. 2020](https://doi.org/10.1088/2632-2153/ab7e1a)
- **UQ benchmark (Varivoda et al. 2023):** across 4 crystal datasets, "popular ensemble methods … are NOT always the best choice for UQ"; code at github.com/usccolumbia/materialsUQ. — [Appl. Phys. Rev. 2023](https://doi.org/10.1063/5.0133528)
- **Conformal prediction with small calibration sets:** the standard marginal-coverage guarantee weakens for small calibration sets; the authors propose a guarantee for a single conformal predictor (preprint, 2025/2026). — [arXiv:2512.04566](https://arxiv.org/html/2512.04566v2). Under data scarcity, no single nonconformity measure wins; the best one is data-dependent. — [arXiv:2410.09894](https://arxiv.org/pdf/2410.09894)
- **GP with monotonic constraints** reduces posterior variance and is recommended for scarce, noisy data with strong monotonic physics. — [Tran et al. 2022](https://doi.org/10.1115/1.4055852)
- An RVE-based XGBoost + SHAP/LIME study of graphene/polymer composites explicitly integrates UQ of meso- and macro-scale input parameters. — [Compos. Struct. 2025](https://doi.org/10.1016/j.compstruct.2025.119292)

### Inferences
- **Practical recipe (inference):**
  1. Fit a GP on log10 k (or on the EMT residual) with an ARD kernel and a noise term; report 68% and 95% intervals.
  2. Fit a monotone GBM with quantile loss (5/50/95%) or a bootstrap ensemble, and calibrate its σ on out-of-group predictions (Palmer).
  3. Wrap either in **group-aware conformal**: compute nonconformity scores from GroupKFold out-of-fold predictions, so coverage reflects "new paper" uncertainty.
  4. Report coverage and interval width per group-CV fold, and a calibration curve (Tran metrics).
- With about 95 groups, a cross-conformal (CV+) scheme over paper folds uses every row for both fitting and calibration, which matters more here than with large data.
- Expect intervals on unseen papers to span roughly a factor of 2–3 in k. If the reported intervals are much narrower than the grouped-CV errors, they are miscalibrated.

### Gaps
- No composite-k ML paper with experimental data was found that reports calibrated intervals or conformal coverage under grouped splits.
- Quantile-regression benchmarks specific to materials k were not found.

---

## 6. Lessons from materials-informatics best-practice guides (leakage, baselines, reporting)

### Takeaway
The best-practice literature agrees: state and justify the split strategy, make it mimic the real use case (here, a new paper or new lab), avoid leakage (no composition or source overlap, preprocessing fitted inside folds), and always compare against trivial and physics baselines. Random-CV scores in materials ML routinely overstate extrapolative performance by about 2–4×.

### Cited Findings
- **Artrith et al. 2021 checklist** (Nat. Chem. 13, 505–508). — [PDF](https://www.coudert.name/papers/10.1038_s41557-021-00716-z.pdf)
  - 1a–c: list all data sources, give versions or access dates, report biases.
  - 2a–c: describe cleaning, quantify removed data, flag and mitigate combining multiple sources.
  - 3a–b: describe representations and compare them with standard feature sets.
  - 4a–c: release software; compare with **simple baselines (1-nearest-neighbour, RF, predicting the mean)** and with state of the art.
  - 5a–c: separate train, validation and test sets; state the split method ("random, cluster- or time-based … Does it mimic anticipated real-world application?"); avoid leakage ("is the same composition present in training and test sets?").
  - 6a–b: release code and reproduction scripts.
  - The text also cites that a single two-parameter neuron matched a 13,451-parameter network on aftershocks (the baseline lesson), and that 14% of Materials Project elastic data was found unphysical (the data-cleaning lesson).
  - It recommends **time-split CV** as prospective-style validation.
- **Meredig et al. 2018 (LOCO-CV):** "Traditional machine learning (ML) metrics overestimate model performance for materials discovery." — [Mol. Syst. Des. Eng. 2018](https://pubs.rsc.org/en/content/articlehtml/2018/me/c8me00012c). Artrith et al. summarise this study: accuracies dropped "substantially (2-4× performance reduction)" under cluster-based splits, and models were "extremely fragile" to new data. — [Artrith 2021](https://www.coudert.name/papers/10.1038_s41557-021-00716-z.pdf)
- **Durdy et al. 2022:** K-means LOCO-CV does not guarantee cluster sizes or chemically sensible clusters, and its stochasticity hurts reproducibility. They propose kernelised LOCO-CV and random-projection baselines. They also note that heavily explored "promising" families bias datasets. — [Digital Discovery 2022](https://pubs.rsc.org/en/content/articlehtml/2022/dd/d2dd00039c)
- **Kapoor & Narayanan 2023:** found leakage in 17 fields affecting **294 papers**, sometimes giving "wildly overoptimistic conclusions." They give an 8-type leakage taxonomy and propose "model info sheets." In one case study, the claimed superiority of ML vanished after the leakage was fixed. — [Patterns 4, 100804 (2023), PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856)
- **scikit-learn guidance:** "The i.i.d. assumption is broken if the underlying generative process yields groups of dependent samples." GroupKFold "ensures that the same group is not represented in both testing and training sets." LeaveOneGroupOut and StratifiedGroupKFold are also available. Preprocessing "should be learnt from a training set," which a Pipeline enforces inside CV. — [scikit-learn docs](https://scikit-learn.org/stable/modules/cross_validation.html)
- **Domain evidence:**
  - Leave-one-source-out cut R² from about 0.46 (10-fold) to about 0.05 for literature PCM-composite k. — [Sci. Rep. 2026](https://www.nature.com/articles/s41598-026-68034-3)
  - SVR and NN had negative CV R² despite high training R², a classic small-data overfitting signal. — [same](https://www.nature.com/articles/s41598-026-68034-3)
- Zhang & Ling: in small data, the effect of data size "is mediated by the degree of freedom (DoF) of model"; a precision–DoF association signals underfitting bias. — [npj Comput. Mater. 2018](https://doi.org/10.1038/s41524-018-0081-z)

### Inferences
- **Validation protocol for the project (inference):**
  - Primary metric: **GroupKFold by DOI** (5–10 folds, repeated with shuffled group assignment), or leave-one-paper-out on log10 k. Report MAE in log10 units, RMSE, R², and the median fold-wise factor error.
  - Secondary checks:
    - Random K-fold, reported only to show the leakage gap.
    - A **leave-filler-family-out** split (e.g., train on BN, test on AlN/Al2O3/hybrids) for extrapolation.
    - A **time split** (train on papers ≤ year X, test on later), as Artrith et al. recommend.
  - Baselines:
    - Predict the training mean.
    - Predict the matrix-class mean.
    - 1-NN on (filler, vol%).
    - Pure Maxwell or Lewis–Nielsen.
    - Linear regression on log k against vol%.
  - Keep all imputation (matrix k, size), scaling, target encoding and feature selection inside the fold pipeline.
- **Model families suited to 260 rows / 95 groups (inference):**
  - Regularised linear or GAM-style models on log k with EMT features (interpretable, low DoF).
  - GP with an EMT mean function.
  - Monotone-constrained gradient boosting (shallow trees, strong regularisation).
  - Random forest as a robust baseline.
  - Avoid deep nets and SVR without strong evidence: they overfit in the closest analogue study.
  - Report SHAP or partial-dependence plots only for the grouped-CV model.
- **Reporting:** include an Artrith-style checklist and a Kapoor-style model info sheet in the course report, covering source papers, cleaning counts, wt%→vol% conversion, imputation rates (e.g., size known for only 71/260 rows, alignment for 29), and the split rationale.

### Gaps
- No materials-informatics guide was found that is specific to *literature-mined composite property* datasets (e.g., rules for weighting rows per paper, or for duplicate loading series). Practitioners must extend the general guidance, for example by down-weighting papers with many rows or using per-group sample weights.
- No published comparison was found of group-weighting schemes for very unbalanced rows-per-paper distributions in materials data.
