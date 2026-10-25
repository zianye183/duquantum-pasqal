# Embedding audit: strong constraints hide weak objective-bearing connections

**New controlled comparison:** [Classical intended-versus-physical QUBO solving](classical_compare/REPORT.md) now shows that changing only the pair interactions eliminates feasible minima in all 60 tested small textbook layouts and all ten tested medium reduced layouts. Medium textbook cases are separately verified with classical bounds. This establishes a static energy-landscape effect; it does not predict quantum sampling probabilities.

**Follow-up testing correction:** The [adversarial testing and tuning review](TESTING_AND_TUNING_REVIEW.md) found that all six checked small transferred textbook models have exclusively infeasible mathematical minima. Their lower fit errors must not be interpreted as a more faithful encoding of the original constrained problem. It also fixed a missing-result reporting bug and quantified a negligible emulator distance-rounding difference. The geometric-error table below remains supported.

## 1. What this is

**The saved interaction errors are numerically correct, but their aggregate score hides severe distortion of the connections that carry clustering information.** This audit independently measures the saved Pasqal geometries and decomposes their target interactions. It does not establish that embedding alone caused poor solutions.

The penalty-density hypothesis needs refinement: the reduced formulation is already fully connected without its balance penalty. In the textbook formulation, capacity penalties add many connections, but do not connect every pair globally. Coefficient strength, not just edge count, is a central concern.

## 2. What was done

Three independent reviews reconstructed physical interactions, reconstructed mathematical terms, and checked interpretation against official conventions. The reconstruction covers 350 saved condition records representing 289 distinct geometries: 261 prepared sequences, 44 submitted sequences, and 45 geometry-only preparation failures. The last group describes proposed layouts, not executed experiments.

There were 217,795 independent scalar pair checks, five passing unit tests, and 44 submitted/prepared sequence comparisons with no coordinate or interaction-constant mismatches. The maximum relative pair discrepancy was approximately \(1.50\times10^{-15}\). Independent term reconstruction checked 384 model copies and 1,680 binary states; coefficient discrepancies were numerical roundoff.

The main scaling comparison contains 336 conditions and 288 distinct fits. Repeated controls and accuracy checks do not count as independent fits. Summaries average three placements within each instance, then average instances: ten small instances and five each at medium and large sizes in the primary cohort. Failed preparations with saved geometry remain included.

## 3. Results

### What the error measures

For full unordered-pair coefficients,

\[
E(x)=c+\sum_i h_ix_i+\sum_{i<j}J_{ij}x_ix_j,\qquad
U_{ij}=\frac{C_6}{r_{ij}^{6}},\qquad
\epsilon_J=\frac{\lVert U-\alpha J\rVert}{\lVert\alpha J\rVert}.
\]

The comparison uses the saved applied scale; independently recomputed least-squares scales are also recorded. Physical interactions are reconstructed from coordinates and the serialized device, rather than copied from optimizer output. Cached errors agree within approximately \(5.11\times10^{-7}\).

These are geometric coefficients from Euclidean distances. Pulser additionally rounds distances to six decimal places; the follow-up measured a maximum absolute change of approximately \(3.27\times10^{-7}\) in the relative-error metric across 289 fits. They should not be described as bit-for-bit emulator coefficients.

Zero error means exact agreement. The error can exceed one. It is neither quantum-state fidelity nor success probability; subtracting it from one is invalid. The conventions agree with [Pulser](https://pulser.readthedocs.io/en/v1.5.4/conventions.html) and [Pasqal's Hamiltonian documentation](https://docs.pasqal.com/qpu-emulators/emumps/v2.2.0/advanced/hamiltonian/).

| Primary formulation | Atoms | Target density | Custom mean relative error | BLaDE mean relative error |
|---|---:|---:|---:|---:|
| Small reduced | 4 | 100% | 0.210 | 0.204 |
| Small textbook | 14 | 50.55% | 0.694 | 0.497 |
| Medium reduced | 20 | 100% | 1.025 | 0.534 |
| Medium textbook | 45 | 34.85% | 1.596 | 0.993 |
| Large reduced | 45 | 100% | 1.319 | 0.370 |
| Large textbook | 80 | 26.90% | 2.557 | 1.201 |

![Overall interaction errors](figures/fidelity.png)

### The most important hidden distortion

In large reduced BLaDE fits, 45 same-customer pairs carry **86.88% of the target squared norm**. These enforce assignment restrictions and contain balance contributions. Their relative error is only **0.130**.

The remaining 945 different-customer pairs carry clustering information as well as balance contributions. Their relative error is **0.965**, despite the overall score of **0.370**. They account for **89.33% of residual squared norm**.

At the unchanged applied scale, their target-squared-weighted mean physical/target strength is **14.56%**. The average of the per-fit median ratios is only **0.296%**. This is systematic weakening, not merely errors scattered evenly above and below target. All five large instances show the same pattern across their three placements. These connections are objective-bearing, not objective-only; the overlapping distance and balance contributions cannot be separately assigned physical residuals.

![Errors separated by the role of each connection](figures/pair_group_errors.png)

### Density and penalty strength are different

A squared sum connects pairs within that sum:

\[
\lambda\left(\sum_i a_ix_i-b\right)^2
=\lambda b^2+\lambda\sum_i(a_i^2-2ba_i)x_i
+2\lambda\sum_{i<j}a_ia_jx_ix_j.
\]

Textbook assignment squares connect vehicle choices for the same customer. Capacity squares connect customers and helper bits within one vehicle. The latter add 30, 180, and 340 connections at small, medium, and large sizes. They do not produce a single complete graph over all bits.

In the reduced formulation, eliminating one vehicle already connects different customers across vehicle choices. Assignment penalties fill the remaining pairs. The balance penalty adds no new edges to these already complete graphs, although it changes their strengths.

To account for overlapping terms without double-counting, the strength attribution uses

\[
s_t=\frac{\langle J_t,J\rangle}{\lVert J\rVert^2},\qquad \sum_t s_t=1.
\]

In large reduced problems, assignment, balance, and distance shares are respectively **83.87%, 9.87%, and 6.26%**. In large primary textbook problems, capacity contributes **99.9792%**, leaving distance only **0.0161%**. These are additive projection shares, not causal shares of error. Transferred penalties change these strengths substantially without changing graph density.

All finite-distance physical pairs interact. For large primary textbook BLaDE fits, error on required edges is approximately **1.201**, while unwanted-edge leakage normalized by the full target norm is only **0.000662**. Here the major measured discrepancy is distortion of required interactions, not unwanted connections alone.

![Density and coefficient strength](figures/density_and_strength.png)

### How tuning fits this evidence

The existing notebook calibration selects the balance weight from 81 logarithmically spaced candidates, using the known optimum to maximize a device-scaled energy margin. The assignment weight follows a sufficient bound, rather than an empirical search. The scaling study's primary reduced settings use an equal-weight balance rule and that assignment bound. Thus these are neither wholly untuned defaults nor a comprehensive held-out optimization.

Optuna is a reasonable tool for the next stage, but the target score matters more than the optimizer brand. Optimizing aggregate interaction error alone could preserve dominant constraint pairs while sacrificing clustering connections. Raw penalized energies also cannot be compared across different penalty weights as if they were the original objective.

An [existing bounded Optuna pilot](../scaling/tuning_pilot/REPORT.md) already compared 40 adaptive and 40 random settings on eight training instances, with eight validation and eight final-test instances. Both searches chose the same initial candidate. Final-test feasible mathematical minima improved from 6/8 to 8/8, while original optima improved from 2/8 to 3/8; validation optima fell from 2/8 to 1/8. It shows no adaptive-search advantage and no physical-performance improvement: it evaluated exact mathematical ground states, with zero cloud submissions.

The recommended next protocol is staged: validate formulation and penalty rules locally; optimize physical placement while retaining separate pair-group errors; then compare a small fixed shortlist of pulse settings in Pasqal Cloud. Select on training instances, freeze before validation and final testing, repeat independent search seeds, and give adaptive and random search equal budgets. Report original feasible solution quality, failure rates, and compute cost together. Use paired placement seeds when comparing settings. Optuna's [reproducibility documentation](https://optuna.readthedocs.io/en/v4.5.0/faq.html) warns that a sampler seed does not make parallel execution or a stochastic objective deterministic.

## 4. Issues and gaps

- This confirms interaction distortion, not its causal contribution to sampling failure. Existing completed small-instance correlations do not consistently associate lower aggregate error with better feasibility.
- Linear controls, pulse evolution, mathematical capacity modeling, and numerical simulation accuracy remain separate concerns. The per-run reconstruction includes actual endpoint linear errors where sequences exist; pair error alone does not describe the full implemented energy.
- Historical notebooks 1–4 do not preserve full original coordinates, coefficients, and applied scales for every run. Their original printed errors cannot all be independently reconstructed. Two older physical penalty follow-ups are recoverable; four ideal-interaction diagnostics are separately classified, not treated as physical layouts.
- Two planned accuracy comparisons lack constructed records because their source preparations failed. Their original source geometries are covered. The 45 geometry-only failures provide no actual pulse fields.
- These measurements concern the saved worktree snapshot. They are not a claim about subsequent results produced by a separate live cloud study, or about hardware performance.

## 5. Current status

The reconstruction, independent checks, aggregation, and visual inspection are complete. No cloud jobs were launched for this fidelity audit, so it incurred no new cloud charges. No audit experiment is running. Earlier cloud spending is outside this audit and is not assumed to be zero.

## 6. Best next step

Run a matched intended-versus-geometric interaction comparison with the same problem, pulse, and linear controls. That isolates the effect of pair distortion before a broad Optuna search. Then tune on separate development instances using the component-sensitive measurements above. Runtime and cloud charges for that experiment have not been measured; this report does not invent a cost estimate. No user input is required to accept or reproduce the completed measurements.

### Reproducible evidence

- [Every reconstructed condition](recomputed/runs.csv), [coverage](recomputed/coverage.json), [independent verification](recomputed/validation.json), and [method](recomputed/METHOD.md).
- [Aggregate results](summary.csv), [instance-level points](instance_points.csv), and [aggregation checks](aggregation_checks.json).
- [Term decomposition and pair-group analysis](term_report.md), [complete group measurements](terms/pair_groups.json), and [independent interpretation](interpretation.md).
- [Earlier notebook audit](../REPORT.md), including confirmed diagnostic bugs, mathematical limitations, and the original six cloud experiments.
