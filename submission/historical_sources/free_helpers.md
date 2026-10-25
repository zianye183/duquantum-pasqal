# Extra atoms as a diagnostic of embedding failure

## 1. What this is

**Extra atoms improved logical-energy matching and substantially increased feasible quantum samples on one medium instance, but did not recover original-optimal solutions.** The controlled correction experiment also shows that both pair interactions and linear biases matter. The global-detuning restriction cannot be treated as part of the pair-matrix error.

This is an exploratory diagnostic on previously studied Track A instances. It is not a new clustering formulation, a benchmark of the best possible auxiliary encoding, or a demonstrated quantum advantage.

## 2. What was done

### Recovered evidence

The [original classical comparison](../fidelity/classical_compare/REPORT.md) found feasible intended minima in all 60 small textbook layouts, all ten medium reduced layouts, and all ten medium textbook layouts. Changing only pair interactions removed every feasible minimum in all of those tested layouts. The [fidelity report](../fidelity/REPORT.md) records the corresponding coefficient errors and their conventions.

The newer sibling-worktree multistart report was also inspected. Its 100 selected medium layouts produced 200 pair-only/global energy systems excluding all feasible ground states. This is an interim report: its main BLaDE study was not reported complete. These observations motivated the present intervention; they are not counted as new experiment repetitions.

### Actual physical auxiliary atoms

Original logical variables and original slack variables retain their meanings. Additional atoms are free helper variables, not extra customers, copied answers, or artificially uncoupled placeholders. Every physical pair interacts through the serialized device's distance law. All atoms share the original layout's final detuning. The target QUBO, its physical scale, and original problem reference are frozen.

For logical state \(x\) and added-atom state \(a\), the static effective energy is

\[
E_{\mathrm{eff}}(x)=\min_a E_{\mathrm{physical}}(x,a).
\]

The helper minimization is exact. It can generate effective linear, quadratic, and higher-order terms. Consequently, comparing an enlarged physical pair matrix directly with the original logical pair matrix would be meaningless.

Positions are fitted to target energies on a fixed combination of random states and low-target-energy states. An additive offset is removed; the target energy scale is not refitted. Using target low-energy states is explicitly **oracle-informed diagnostic training**, not a deployable low-cost encoder. Separate held-out bitstrings are used for fit-error reporting. Every logical bitstring is then enumerated to classify all logical ground states and measure the best feasible versus infeasible physical energies.

The static controls are the saved physical layout, a newly fitted layout with no helpers, and layouts with helpers. Newly fitted arms use matched iteration budgets, not matched runtime or function-evaluation counts. Each new condition has two starts. The representative restart in the static tables is selected by training loss, never by held-out error or ground-state feasibility. No sampled answer is repaired.

### Completed static experiments

- Three small textbook instances, 14 logical bits, adding zero/two/four atoms; 350 optimizer iterations per start.
- All five saved medium reduced instances, 20 logical bits, adding zero/two/four atoms; the same iteration budget.
- All five medium instances, adding zero/four/eight atoms; a separate 1,500-iteration budget.
- 48 initial-study fits and 30 longer-study fits: **78/78 completed**. The earlier 12-fit implementation pilot repeats two of these instances and is not additional independent evidence.
- The 45-logical-bit medium textbook model was recovered as prior evidence but was not included in the new exhaustive auxiliary experiment.

All reported geometries satisfy the minimum separation, maximum radius, and Pulser register checks. The quantum jobs additionally use valid half-filled trap layouts; unoccupied traps are not counted as atoms.

### Implementation checks

Independent checks compared helper elimination with full-state enumeration, checked coordinate derivatives, verified the original decoder and energy conventions, and checked cloud atom ordering before decoding. A close-distance derivative inconsistency in the new preliminary fitting code was corrected before either main study; the preliminary source is retained separately. The correction-control study passed 49,152 independent matrix evaluations with maximum discrepancy approximately 1.48e-12. Local quantum evolution was independently checked against QuTiP as detailed below. These checks support the implementation used here; they do not prove the geometry search finds the best possible encoding.

## 3. Results

### Medium: adding atoms helps energy fitting more reliably than solution quality

The table uses the longer budget and training-selected restarts across five independent medium problems.

| Method | Physical atoms | Mean held-out effective-energy error | Feasible logical minima | Original-optimal logical minima |
|---|---:|---:|---:|---:|
| Saved layout | 20 | 0.6684 | 0/5 | 0/5 |
| Refit, no helpers | 20 | 0.3633 | 1/5 | 0/5 |
| Refit, four helpers | 24 | 0.3211 | 1/5 | 0/5 |
| Refit, eight helpers | 28 | 0.3008 | 2/5 | 0/5 |

The error is centered effective-energy RMSE divided by held-out target-energy standard deviation. **It is not the earlier relative pair-matrix error.** It can be compared between rows here, but not numerically with the previous fidelity table.

Eight helpers lower this error by approximately 17% relative to the no-helper control with the same iteration limit. Most improvement from the original layout already comes from changing the fitting objective and optimizing again without helpers. The two feasible selected eight-helper minima have original clustering costs **68.48% and 70.98% above the exact reference**.

All 30 longer-budget fits reached their iteration limit. These are bounded-search outcomes, not converged or globally optimal embeddings. The shorter medium study had feasible selected minima in 1/5, 2/5, and 2/5 cases for zero/two/four helpers, respectively; longer average-energy optimization does not monotonically improve feasibility.

### Small textbook encoding

Across three small instances, held-out effective-energy error falls from 0.8347 for the saved layout to 0.5473 with no-helper refitting, 0.4735 with two helpers, and 0.4152 with four helpers. **None of the selected physical ground states is feasible: 0/3 throughout.**

![Paired effective-energy errors and ground-state feasibility](comparison.png)

### Helpers often act as bias adjustments

Of the 40 helpers in the five selected eight-helper layouts, **27 are excited in every conditional logical-state minimum**. Those fixed helpers directly contribute a constant and individual linear shifts to logical atoms and other helpers. Their direct contribution adds no pair term; changed biases on state-dependent helpers can still alter effective logical interactions indirectly.

For the first medium eight-helper example, an independent exact Boolean Fourier projection over all 1,048,576 logical states gives a projected logical pair-matrix relative error of **0.7672**. Higher-order terms contribute only about **0.000327% of the effective-energy variance**. This example has not become a faithful reproduction of the original pair matrix, even though its effective-energy error and feasibility improved. Auxiliary occupation here is a static conditional-minimum property, not a quantum measurement probability.

### Controlled correction distinguishes pairs from fields

The separate [correction study](interpolation/REPORT.md) exhaustively evaluated 192 energy systems and 127,008,768 state-energy combinations. It interpolates from physical to target coefficients without claiming those intermediate matrices are physically realizable.

| Fully corrected coefficients | Small slack feasible minima | Medium reduced feasible minima |
|---|---:|---:|
| Correct pairs, retain original shared field | 0/3 | 2/5 |
| Correct pairs and individual target fields | 3/3 | 5/5 |

With exact individual fields supplied throughout, correcting 99% of the pair error already restores feasible minima in every tested instance. When both fields and pairs are interpolated together, all three small cases are still infeasible at the 99% grid point and become feasible at 100%. This is a sampled grid, not a certified transition threshold; some medium trajectories are nonmonotonic.

The intended medium reduced model is itself original-optimal in only four of the five cases. Full correction preserves that known formulation defect rather than hiding it.

### Quantum simulations

All quantum runs here are noiseless simulations. All physical dynamics use the actual larger Hamiltonian, including quantum evolution of the helper atoms. The effective minimum-over-helpers energy is **not** substituted into the simulator. All arms use the same new six-microsecond sine-amplitude schedule and linear detuning sweep. The saved-layout arm preserves coordinates and endpoint field, not historical notebook shot rates.

The initial quantum pilot freezes the first optimizer start in each arm. This differs from the training-selected static table: on the chosen small instance, the static no-helper and four-helper representatives use the second start. The two-helper representative happens to match. The subsequent longer-fit medium quantum pair uses training-selected starts for both conditions. Quantum results should therefore not be interpreted as sampling every representative in the static table.

The initial six Pasqal Cloud jobs have completed, with 2,000 shots each. Small jobs use full state vectors; medium jobs use a matrix-product-state approximation:

| Physical arm | Atoms | Feasible shots | Original-optimal shots |
|---|---:|---:|---:|
| Saved layout | 14 | 0/2000 | 0/2000 |
| Refit, no helpers | 14 | 0/2000 | 0/2000 |
| Two helpers | 16 | 36/2000 (1.8%) | 0/2000 |
| Four helpers | 18 | 0/2000 | 0/2000 |
| Medium saved layout | 20 | 0/2000 | 0/2000 |
| Medium four helpers, shorter fit | 24 | 6/2000 (0.3%) | 0/2000 |

Zero observed successes do not establish zero underlying probability. An independent local state-vector calculation gives approximately **1.498%** feasible probability for the two-helper arm. The distribution change from halving its integration step is approximately 0.000263 in total variation. Thus the small feasibility improvement is corroborated, but remains low and does not produce observed original-optimal solutions. The six feasible medium samples remain provisional: the stronger-accuracy check below covers different, longer-budget layouts, not this four-helper arm.

Local ideal controls on the same small instance and pulse distinguish two changes:

| Emulator control | Feasible probability | Original-optimal probability |
|---|---:|---:|
| Exact pair interactions, original shared field | 0.000001514% | 0.000000748% |
| Full target interactions and individual fields | 7.0072% | 3.5784% |

Across all six local arms, the largest full-distribution change between the two integration step sizes is 0.000394 in total variation. An independent three-atom QuTiP comparison differs by 0.0000573. These checks support the small-instance integration accuracy; they do not certify medium MPS accuracy.

The full-target control confirms that correcting the full Hamiltonian substantially improves this small-instance dynamics. It still gives only 7% feasibility under the fixed pulse, so encoding quality is **not the only limitation**. Correcting only the pair matrix performs worse than the original physical arm in this particular dynamical comparison.

The matched longer-fit medium pair has now also completed:

| Longer-fit medium arm | Atoms | Feasible shots | Original-optimal shots |
|---|---:|---:|---:|
| Refit, no helpers | 20 | 30/2000 (1.5%) | 0/2000 |
| Eight helpers | 28 | 1256/2000 (62.8%) | 0/2000 |

This is a large feasibility improvement on the first preselected medium instance, with each condition selected by training loss. It remains a single-instance pilot and does not establish high-quality optimization: even the eight-helper static minimum costs 68.48% above the exact original optimum.

The medium no-helper simulation samples its **infeasible physical ground state in 95.6% of shots** at bond dimension 128 and **96.05%** at 256. The eight-helper simulation samples its physical ground state in **62.25%** of shots at 128; this minimum is feasible but costs 68.48% above the original optimum. Thus these runs often find the minimum of the Hamiltonian actually simulated. The encoded energy ordering makes that minimum the wrong answer. The lowest physical energy among original-optimal clusterings lies 110.11 radians per microsecond above the no-helper physical minimum and 75.565 above the eight-helper physical minimum.

Scoring the first, bond-dimension-128 batches against the original clustering objective gives:

| Longer-fit medium arm | Feasible sample count | Best observed cost gap | Median feasible cost gap |
|---|---:|---:|---:|
| Refit, no helpers | 30 | +38.88% | +62.66% |
| Eight helpers | 1256 | +50.92% | +68.48% |

The exact reference cost is 438.923. The added-atom arm samples feasible solutions much more often, but **1,251 of its 1,256 feasible samples (99.60%) have the distorted static-ground-state cost, 68.48% above the reference.** Its observed best and median costs are worse in these first batches. The no-helper arm supplies very few feasible samples, however: its separate bond-256 batch has best and median gaps of 52.86% and 77.99% across only 20 feasible shots. This variability prevents a general conclusion that adding atoms makes solution quality worse. The robust issue is concentration far above the optimum, not the ordering of noisy conditional medians. Exact 95% binomial intervals for the initial feasibility rates are 1.014–2.134% and 60.639–64.923%; these intervals quantify finite-shot uncertainty, not MPS approximation error.

The initial four medium jobs use bond dimension 128, precision 1e-8, 10 ns steps, and 2,000 shots each. Two otherwise identical longer-fit jobs at bond dimension 256 have now completed:

| Matched medium arm | Feasible at bond 128 | Feasible at bond 256 | Optimal shots across both |
|---|---:|---:|---:|
| Refit, no helpers | 30/2000 (1.5%) | 20/2000 (1.0%) | 0/4000 |
| Eight helpers | 1256/2000 (62.8%) | 1270/2000 (63.5%) | 0/4000 |

The large feasibility improvement survives doubling the bond limit. Exact 95% binomial intervals overlap within each arm: the eight-helper bond-256 interval is approximately 61.35–65.61%. Changes in sampled physical and intended mean energies are also within sampling uncertainty. For the eight-helper check, 1,264 of 1,270 feasible samples again have the cost 68.48% above optimum. Its physical-ground-state frequency is 62.95%, consistent with the initial 62.25%.

This is a bounded numerical robustness check, not proof of complete simulator convergence. The medium timestep remains 10 ns in both settings; timestep convergence and full-distribution convergence were not checked. All ten cloud jobs produced **20,000 total shots and zero observed original-optimal clusterings**.

## 4. Issues and gaps

- This is a free-helper fitting heuristic, not the literature's constructive wire/crossing encoding. Failure here does not rule out larger or differently designed redundant encodings.
- Added atoms can improve a final classical energy landscape while making the quantum evolution harder. Static feasibility and quantum success are separate measurements.
- Shared-field mismatch is independently destructive on the tested small problems and several medium problems. Pair fidelity alone is insufficient.
- Two starts and five medium instances are limited coverage. Instance outcomes have been seen before; no fresh-instance generalization is claimed.
- Exact logical enumeration makes the static statements definitive for these fitted layouts, but auxiliary degeneracies are marginalized; counts are logical ground-state counts.
- The diagnostic accesses low-target-energy states during fitting. Its classical work must not be presented as computationally light production preprocessing.
- The matched medium pair passed the reported bond-limit comparison for sampled feasibility and mean energies. Medium timestep convergence remains untested, as does the accuracy of the separate short-fit four-helper arm.
- Cloud charges are unavailable. Submitted jobs are not assumed free.

## 5. Current status

**Complete as of 7:12 am ET on October 25, 2026. Nothing is running.** The 78-fit static study, 192-system correction control, all six local quantum controls, eight primary cloud simulations, and two stronger-accuracy medium checks are complete. Cloud charges are unavailable. See [initial cloud status](quantum/cloud/summary.json), [medium follow-up status](quantum_extended/cloud/summary.json), and [accuracy-check status](quantum_convergence/cloud/summary.json) for timestamped records.

Recorded fit-and-evaluation times total 64.79 seconds for the short study and 322.45 seconds for the longer study. These exclude data preparation, imports, independent reviews, and quantum evolution; they are not total session duration. The correction experiment recorded 105.11 seconds. Local quantum solvers recorded 682.03 seconds. No total-cost or full-wall-time claim is made.

## 6. Best next step

The present evidence supports an encoding bottleneck with both pair and field components. Extra atoms can recover feasibility, but **feasibility alone does not show that the original optimization problem is solved faithfully**. The next construction should explicitly preserve low-energy feasibility and the original objective, rather than selecting on average energy error alone.

The recommended next fitting experiment would penalize two specific errors: infeasible states below good feasible states, and expensive feasible states below cheaper feasible states. Exact enumeration can periodically supply the worst current counterexamples. A bounded comparison would use 32 local fits: four medium cases with correct intended optima, zero/eight helpers, two starts, and current/ranking-based objectives. Keep the known formulation-defective fifth case separate. Choose layouts by their worst ordering violation; retain energy RMSE as a secondary diagnostic. Only consider further quantum submissions after the fitted physical minima preserve better original solutions. This follow-up is not launched, has unmeasured runtime, and would initially require no cloud jobs. It remains oracle-informed research rather than a proven production encoder.

### Reproduction and evidence

- [Auxiliary fitting and checks](fit.py), frozen protocols in [short study](study/protocol.json) and [longer study](extended/protocol.json).
- [Aggregate analysis](analyze.py), [machine-readable summary](summary.json), [all restart records](summary.csv).
- [Correction control](interpolation.py), [correction validation](interpolation/validation.json).
- [Quantum runner](quantum_pilot.py), [medium follow-up](quantum_extended.py), [frozen initial cloud manifest](quantum/prepared/manifest.json).
- [Completed medium accuracy check and cost distributions](quantum_convergence/REPORT.md), [machine-readable accuracy comparison](quantum_convergence/comparison.json).
- [Independent dynamics check](quantum/independent_integrator_check.json).

Run local scripts using the existing project Python environment. The cloud runner only submits with an explicit submit action and never automatically retries an uncertain submission. Do not rerun preparation over submitted manifests. The fit protocols reject changed source/configuration on resume. The original implementation pilot retains its source snapshot; the main studies use the corrected close-distance gradient.
