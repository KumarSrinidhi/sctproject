README Dataset: Thermal Conductivity of Polymer Matrix Composites for
EVF Modeling

Associated Manuscript: Effective Volume Fraction as a State Descriptor
of Composite Thermal Conductivity Dimitrios Anastasiou, Patras, Greece

1.  Dataset Overview

This dataset contains literature-derived thermal conductivity
measurements for polymer matrix composites reinforced with particulate,
nano-scale, and hybrid fillers. It was constructed to evaluate
descriptor-level corrections through the Effective Volume Fraction (EVF)
state descriptor applied to classical micromechanical conductivity
models.

The dataset currently includes:

-   293 composite data points
-   56 independent composite series
-   Multiple filler classes (carbon-based, ceramic, hybrid systems)
-   Broad matrix conductivity range
-   Wide filler conductivity contrast

Each composite series corresponds to a distinct matrix–filler system
with conductivity reported as a function of reinforcement volume
fraction.

2.  File Structure

Main file: EVF_Thermal_Conductivity_Dataset.xlsx

Each row corresponds to one experimental data point.

Representative columns include:

-   Composite_Series — unique series identifier
-   System — matrix–filler system description
-   Vf — nominal reinforcement volume fraction (fractional form)
-   k_exp_WmK — experimentally reported composite conductivity
-   k_matrix_WmK — matrix thermal conductivity
-   k_filler_WmK — intrinsic filler thermal conductivity
-   Filler_Class — categorical descriptor
-   Filler_Size — micro / nano / hybrid
-   Dispersion_Descriptor — as reported in source
-   Orientation — isotropic / aligned (if reported)
-   Temperature_C — test temperature
-   Citation — bibliographic source

Volume fractions originally reported in percent were converted to
fractional representation prior to modeling.

3.  Data Curation Protocol

3.1 Inclusion Criteria

Datasets were included only if:

-   Composite conductivity was explicitly reported.
-   Matrix conductivity was explicitly reported.
-   Filler loading was reported as volume fraction or convertible from
    weight fraction.
-   Measurements were performed under steady-state or quasi-steady-state
    conditions.

Only datasets reported at or near room temperature (20–30 °C) were
retained to minimize temperature-induced variability unrelated to
reinforcement participation.

4.  Treatment of Material Parameters

4.1 Filler Conductivity Assignment

In 12 composite series, intrinsic filler conductivity was not explicitly
reported in the source publication.

In these cases:

-   Literature-consistent intrinsic conductivity values specific to the
    filler type were adopted.
-   Values were selected from peer-reviewed sources reporting intrinsic
    conductivity for the same material class.
-   A single intrinsic conductivity value was assigned per series and
    held constant across all reinforcement levels.
-   Adopted values correspond to bulk intrinsic material properties
    rather than composite back-calculation to avoid circular fitting.

No matrix conductivities were inferred; only explicitly reported values
were used.

4.2 Interfacial Thermal Resistance (Nan Model)

For the Nan interfacial-resistance formulation:

-   Reported interfacial thermal resistance values were used directly
    when available.
-   When no interfacial resistance value was reported, the model was
    evaluated under ideal-interface assumptions.
-   No interfacial resistance parameters were fitted or optimized.
-   No additional transport parameters were introduced.

4.3 Temperature Consistency

All included datasets were measured at or near room temperature (20–30
°C). No temperature normalization or correction was applied.

5.  Effective Volume Fraction (EVF) Determination

For each composite series and for each baseline micromechanical model
independently:

1.  Reference point selection:

    -   Series with four or fewer non-zero reinforcement levels ->
        highest volume fraction selected.
    -   Series with more than four non-zero reinforcement levels ->
        second-highest volume fraction selected.

2.  The baseline model equation was inverted numerically at the selected
    reference point to determine the effective participation fraction
    reproducing the experimental conductivity.

3.  The morphology exponent was computed as:

    z = ln(Vf) / ln(Vf_eff)

4.  The resulting exponent z was held constant for all remaining data
    points within the same series.

No cross-series fitting, global regression, or multi-point optimization
was performed.

6.  Modeling Scope

The dataset was used to evaluate:

-   Voigt–Reuss–Hill mixture model
-   Maxwell dilute inclusion model
-   Bruggeman symmetric effective medium model
-   Nan interfacial-resistance mean-field model

Percolation-type models were excluded due to threshold singularities and
limited invertibility across heterogeneous literature datasets.

7.  Reproducibility

All calculations were performed using fractional volume fraction values.

No regression fitting or model-parameter optimization was applied beyond
deterministic single-point EVF exponent extraction.

The EVF substitution was implemented by replacing the nominal
reinforcement fraction Vf with Vf^(1/z) within each baseline model
formulation, without altering constitutive structure.

8.  License

This dataset is distributed under the Creative Commons Attribution 4.0
International License (CC BY 4.0).

You are free to:

-   Share — copy and redistribute the material in any medium or format
-   Adapt — remix, transform, and build upon the material for any
    purpose, even commercially

Under the following terms:

-   Attribution — You must give appropriate credit to the author
    (Dimitrios Anastasiou), provide a link to the license, and indicate
    if changes were made.
-   No additional restrictions — You may not apply legal terms or
    technological measures that legally restrict others from doing
    anything the license permits.

Full license text: https://creativecommons.org/licenses/by/4.0/

© Dimitrios Anastasiou
