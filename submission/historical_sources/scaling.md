# Pasqal clustering scaling study — final report

**Complete: 301 distinct cloud simulations, 602,000 measurements, and independent rescoring with zero mismatches. The configured methods perform poorly at larger sizes, but incomplete tuning and numerical discrepancies prevent a claim about their best achievable performance.**

## 1. What this is

This study tests whether the earlier promising single-instance results generalize across problems, custom and BLaDE atom placement, and larger problem sizes. All sampled measurements come from cloud emulators. Their interactions are calculated from atom distances; the primary sequences do not substitute the desired interaction matrix. The main comparison uses fixed parameter-selection rules and a common pulse policy to compare atom placement. Vendor-specific pulse optimization and best achievable tuned performance remain unmeasured.

## 2. What was done

Prepared 20 distinct, feasible, capacity-active problems with independent random seeds within each size: ten with four customers, five with ten customers, and five with fifteen customers. The reduced encoding uses 4, 20, and 45 atoms; the textbook encoding uses 14, 45, and 80 atoms. Both placement methods receive three placement seeds per problem, giving 240 primary conditions. Three seed values recur across sizes, so the twenty instances use seventeen distinct seed values. Results and uncertainty are calculated separately by size; no pooled cross-size independence is claimed.

A separate transfer test applies penalty ratios selected on the earlier development instance to six small, three medium, and three large problems. It compares shared and individual atom controls, two placement seeds, and both placement methods. Individual controls are emulator-only. This adds 96 conditions. Twelve unique simulator accuracy checks have fourteen references because two checks are reused, with no duplicated statistical weight.

Exact clustering and routing references are computed independently and used for evaluation. Optimal clustering means zero requested relative gap, \(\epsilon=0\), with absolute numerical tolerance \(10^{-8}\). Best clustering gap, independently best routing gap, and the routing gap of the best-clustering sample are different measures; none is replaced by zero when no feasible sample exists. The primary penalty rules use instance data and an independently constructed feasible assignment, not the reference optimum. Invalid assignments are counted as failures; quantum samples are not repaired classically.

## 3. Results

### Completed small primary test

All 120 small primary conditions completed: ten independently generated problems within this size, three placements per method and encoding, and 240,000 measurements. Rates first average placements within each problem. Every requested small condition delivered measurements.

| Encoding and placement | Atoms | Feasible clustering | Optimal clustering |
|---|---:|---:|---:|
| Reduced, BLaDE | 4 | 38.63% | 28.68% |
| Reduced, custom | 4 | 45.53% | 25.65% |
| Textbook, BLaDE | 14 | 2.94% | 0.00% |
| Textbook, custom | 14 | 0.57% | 0.56% |

The textbook model produced no exactly satisfied slack equalities in either placement method. Its poor performance here is a measured result for the conservative penalties and fixed global pulse, not evidence that fourteen atoms cannot be simulated or that no tuned textbook implementation works. Instance variation is substantial: for example, the BLaDE reduced optimal-clustering mean has an instance-bootstrap interval of 0.11–57.29%, while custom has 6.31–48.88%. Zero observed successes do not prove zero underlying probability.

![Completed small primary comparison](plots/primary_small_completed.png)

### Completed small transfer test

All 48 small transfer conditions completed, with 96,000 measurements across six independent problems. Each reported mean first averages the two placements within a problem, then averages problems.

| Placement and controls | Feasible clustering | Optimal clustering |
|---|---:|---:|
| Custom, shared | 22.70% | 13.67% |
| Custom, individual | 33.96% | 13.96% |
| BLaDE, shared | 8.54% | 8.51% |
| BLaDE, individual | 21.78% | 21.18% |

Individual controls improved BLaDE optimal-clustering success by 12.66 percentage points, with a paired instance-bootstrap interval of 3.73–23.70 points. The corresponding custom improvement was 0.29 points, with an interval spanning zero. These six-instance intervals are descriptive and remain uncertain.

![Completed small transfer comparison](plots/transferred_small_completed.png)

On these same six problems, uniform random assignment achieved 31.23% feasibility and 12.74% optimal clustering; a balanced-cardinality sampler achieved 72.38% and 27.55%. A deterministic greedy method found feasible solutions on all six problems and optimal clusterings on two. Sampling budgets differ: each randomized classical method uses three sets of 2,000 proposals per problem, each quantum variant uses two sets of 2,000 measurements, and greedy uses one candidate. Classical proposals start with valid assignments. These comparisons do not establish quantum advantage.

Decoded feasibility is distinct from satisfying every auxiliary slack equality. In the individual-control small runs, exact slack satisfaction was only 0.0708% for custom placement and 0.0125% for BLaDE. Shared-control variants recorded none.

### Completed medium and large transfer test

The entire transferred main cohort is resolved: 84 completed simulations and twelve preparation failures, delivering 168,000 of 192,000 requested measurements. The failures are six large custom geometries, each requested with two control modes; they are not twelve independent geometry failures.

| Size and placement | Shared-control feasibility | Individual-control feasibility | Optimal clustering |
|---|---:|---:|---:|
| Medium, custom | 0 / 12,000 | 0 / 12,000 | None observed |
| Medium, BLaDE | 103 / 12,000 (0.858%) | 117 / 12,000 (0.975%) | None observed |
| Large, custom | Preparation failed | Preparation failed | Unmeasured |
| Large, BLaDE | 0 / 12,000 | 0 / 12,000 | None observed |

Each measured cell covers three independent problems and two placements per problem. Medium custom and large BLaDE returned no valid assignment codes. Medium BLaDE's paired feasibility difference between individual and shared controls was 0.117 percentage points, with an instance-bootstrap interval of −0.725 to 1.025 points. These transferred penalties and individual controls did not rescue larger-case performance under this fixed protocol; they do not establish a tuned or hardware scaling limit.

Medium BLaDE found feasible candidates on all three problems, but its best clustering gaps remained 17.92–51.13% with shared controls and 11.30–46.40% with individual controls. Independently best routing gaps and routes associated with best clustering are reported separately in the [complete transfer interpretation](analysis/TRANSFERRED_FINAL_INTERPRETATION.md). All large-instance and medium-custom gaps are undefined because no feasible candidate was measured. All accuracy references are resolved: eight unique comparisons completed and four were blocked by preparation; two additional references reuse results.

![Complete transferred main cohort, including preparation failures](plots/transferred_success_rates.png)

### Completed interaction-geometry comparison

The coupling error compares the realized pair interactions with a scaled target, using only off-diagonal pairs:

\[
\epsilon_J=\frac{\lVert U-\alpha J\rVert_F}{\lVert\alpha J\rVert_F},\qquad \alpha=\frac{\sum_{i<j} U_{ij}J_{ij}}{\sum_{i<j}J_{ij}^{2}}.
\]

Here the diagonal is excluded, and the Frobenius norm sums squared entries. The scale is fitted by least squares. Lower error is better. This is a coefficient error, not quantum-state fidelity. Penalty terms contribute to the same norm, so it is not a separate guarantee that the original clustering objective is preserved. All fitted geometries are included, even those that subsequently fail preparation. Three placement seeds are averaged within each independent problem.

| Problem size and encoding | Custom mean error | BLaDE mean error |
|---|---:|---:|
| Medium, reduced | 1.025 | 0.534 |
| Medium, textbook | 1.596 | 0.993 |
| Large, reduced | 1.319 | 0.370 |
| Large, textbook | 2.557 | 1.201 |

The custom procedure directly minimizes this relative error plus geometry penalties. BLaDE uses a different force-based placement procedure. Their computational budgets and convergence behavior differ; these results compare the configured implementations, not their best possible performance.

![Interaction fidelity across problems](plots/embedding_fidelity.png)

Every physical pair interacts. The density figure separately shows the fraction of target pairs that are nonzero and the fraction of physical interactions reaching one percent of the strongest pair interaction. The latter threshold is descriptive: the simulator does not discard weaker interactions.

![Target and physical interaction density](plots/coupling_density.png)

### Implementation checks

Known optimal assignments were independently constructed and recognized correctly for all 20 problems and both encodings. All 340 assignment cases and 1,360 atom-order checks passed. All 336 saved model checks matched expected energy, with maximum absolute discrepancy \(4.71\times10^{-10}\). All 293 prepared atom-label mappings checked correctly.

These checks rule out the tested encoding and ordering errors as explanations for the observed results. They do not establish physical fidelity or correctness of every untested state.

A separate raw-measurement verifier recomputes assignment validity, capacity feasibility, coordinate-based clustering costs, routing summaries, optimality rates, and all three gap measures without importing the main scorer. The latest independent check covers 301 unique simulation results and 602,000 measurements, with zero mismatches. Reused references are checked but do not add independent measurements. Exact clustering references and per-subset tour costs are reused from the independently checked reference calculations. The final check covered 303 references pointing to 301 unique raw sources; it does not establish simulator convergence.

### Larger simulations

The medium reduced-encoding BLaDE group has completed all fifteen conditions across five independent problems and three placements each. It produced 1,105 feasible measurements out of 30,000 (3.68%), with no original-optimal clustering. Its instance-bootstrap feasibility interval is 0.0067–9.78%, reflecting substantial variation across only five problems. On one medium problem, feasible-measurement rates ranged from 0.45% to 35.95% across the three placement seeds; two other problems produced none in all three placements. The matching custom group is complete and produced six feasible measurements out of 30,000 (0.020%), with no original-optimal clustering. All fifteen medium textbook custom simulations also completed, producing no feasible measurements; all fifteen medium textbook BLaDE conditions failed preparation and have no measured success rate.

The large reduced-encoding BLaDE group has also completed all fifteen conditions across five problems, producing 49 feasible measurements out of 30,000 (0.163%) and no original-optimal clustering. Its instance-bootstrap feasibility interval is 0.0067–0.4433%. All fifteen matching large custom conditions have also completed: none of their 30,000 measurements was a valid assignment code, feasible clustering, or original-optimal clustering. These are the configured methods under the tested approximate simulation policy; detected observable discrepancies limit claims about exact dynamics.

All fourteen executable large textbook BLaDE placements completed with zero feasible or optimal clusterings in 28,000 measurements; one additional placement failed preparation. All fifteen large textbook custom placements failed preparation. These failures have undefined measured success, not a measured zero probability. Across both main cohorts, no medium or large run found an optimal clustering.

![Final primary feasibility and optimal-clustering results](plots/success_rates.png)

![Delivered results and preparation failures](plots/pipeline_coverage.png)

Successful 45- and 80-atom cloud simulations demonstrate that execution at these sizes is possible. Full-bitstring distribution comparisons are inconclusive because sparse sampling produces large empirical differences even under the same distribution. Agreement on feasibility does not prove numerical convergence.

**Supplementary observable checks detect discrepancies.** An exploratory analysis of the eight completed accuracy pairs found compression-setting differences in the 45-atom reduced custom case and the 80-atom transferred BLaDE case with individual controls. Seven atom-occupation differences survived a conservative joint multiple-testing correction; the largest confirmed change was 9.5 percentage points. The 45-atom case also showed a changed excitation-count distribution, with corrected probability 0.0168. An independent recount and alternative exact calculation confirmed the findings. Both affected cases still had zero feasible measurements at both settings. The other four larger comparisons showed no corrected observable differences. The two completed 20-atom comparisons between state-vector simulation and compression limit 64 showed no corrected observable differences; this non-detection does not certify convergence at larger sizes.

Saved sequences match within each pair. For the six compression-limit comparisons, saved settings differ only in compression and observable identifiers. The two 20-atom reference comparisons intentionally change simulator backend; their compressed settings also specify a time step. Complete submitted artifacts are unavailable for the two detected pairs, and provider version and sampling-seed independence are not independently established. These are confirmed exploratory output discrepancies under the stated sampling assumptions, not a proof that compression is the only cause or that the larger setting is accurate. They strengthen the numerical limitation on interpreting larger-case performance. [Methods, all results, and provenance limits](analysis/ACCURACY_OBSERVABLES.md).

### Bounded Optuna pilot: mathematical model only

**How the parameters were chosen:** the original notebook searched 81 candidate balance weights using the known optimal answer. That is an answer-dependent diagnostic, not a deployable tuning procedure. The scaling benchmark instead freezes the following rules:

| Parameter | Current choice | What it establishes |
|---|---|---|
| Reduced balance weight, \(\mu\) | Match average objective and load-penalty pair scales | A heuristic; no capacity-feasibility guarantee |
| Reduced assignment penalty, \(M\) | Conservative analytic bound when invalid assignment codes exist | Protects assignment encoding under its assumptions; not capacity or original optimality |
| Textbook assignment and capacity penalties | Independently feasible objective bound, rounded upward with a margin | Conservative logical penalties; no guarantee of physical implementation fidelity |
| Transferred textbook penalties | Preserve ratios fitted on one earlier development instance | Tests transfer; not a broadly validated optimum |
| Pulse and placement settings | Fixed common pulse and configured placement budgets | A reproducible baseline; not jointly optimized performance |

Optuna would search these settings, but the search must be scored on original feasibility and clustering quality across training instances, then checked on separate validation and test instances. Optimizing the encoded energy alone can reward the wrong model.

A separate local pilot evaluated 40 Optuna trials and 40 random-search trials on fresh six-customer, three-vehicle problems, with eight training, eight validation, and eight final-test instances. It enumerated all 4,096 reduced-encoding bit states per problem; it did not simulate atom dynamics or collect quantum measurements.

Both searches selected the same initial random candidate, so this pilot shows no advantage of Optuna over random search. On the final test set, the selected parameters increased the number of problems whose ground states were feasible from six to eight out of eight, and those with optimal original clusterings from two to three. On validation, feasibility remained seven out of eight while optimal clustering decreased from two to one. These small, mixed results support investigating parameter sensitivity, not claiming a robust tuning improvement.

The selected assignment penalty is below the conservative bound and loses its formal guarantee. All selected and baseline ground-state calculations were independently checked against the full polynomial. The 80 trials took 2.454 seconds of local computation; no cloud jobs or quantum measurements were used. [Pilot protocol and results](tuning_pilot/REPORT.md).

## 4. Issues and gaps

- **Parameter tuning is incomplete.** The reduced load-balancing weight follows an equal-coupling heuristic; its assignment penalty follows a conservative bound. Textbook penalties use a feasible-solution bound. Transferred penalties retain ratios from one development instance. Pulse duration is fixed at four microseconds.
- **The original notebook's parameter search used the known optimum.** It searched 81 balance weights and selected by an answer-dependent margin. The frozen cloud protocol avoids that leakage but has not undergone training/validation tuning. The separate ideal-model pilot does use training, validation, and test splits.
- **The fixed reduced model does not respond to capacity changes.** Holding customer data and vehicle count fixed, changing capacity changes only an additive energy constant. Both current parameter rules ignore capacity. This was verified against all 20 saved models and 3,065 binary strings, including invalid codes. Feasibility can therefore change while the modeled energy rankings remain unchanged. A capacity-dependent tuning rule can change those rankings, but the squared load-balancing term still does not enforce an upper-capacity constraint. [Derivation and verification](analysis/CAPACITY_DEPENDENCE.md).
- **Custom initialization is problematic.** All 45- and 80-atom starts use a square too small to satisfy the minimum spacing. Every one of the 120 examined 80-atom restarts exhausted its iteration budget. A separate matched diagnostic completed 120 fits with 960 restarts using feasible lattice-based starts under the same budget. It did not improve average interaction fidelity in any group; every paired uncertainty interval included no change. Usable layouts remained 105 out of 120, with all fifteen 80-atom layout failures remaining. This alternative does not rescue the observed scaling problem. The original comparison remains intact.
- **Interaction fidelity omits control errors.** Shared controls cannot reproduce heterogeneous individual coefficients. Individual controls fix that part but leave interaction errors.
- **Preparation failures remain in the ledger.** A failed layout search is evidence about this implementation, not proof that no valid layout exists.
- **Cloud execution failures are separate from poor samples.** Four initial jobs failed without useful provider error details. Controlled retries and other original-path jobs succeeded, so the cause remains unresolved. Original failed attempts are retained, and verified retries count only once per scientific condition.
- **Coverage is resolved, but generalization remains limited.** All requested conditions have results or preparation-failure explanations. Only five primary and three transferred problems per larger size were tested. Bootstrap intervals from all-zero observations do not establish a zero underlying success probability.

## 5. Current status

Nothing is running for this study. The campaign began October 24 at 10:03:56 pm ET and its last cloud execution ended October 25 at 12:03:59 am ET: **2 hours, 3 seconds elapsed**. Summed execution across overlapping attempts was 21 hours, 33 minutes, 41 seconds; this is not billed time. **Charges remain unknown.**

| Cohort | Requested unique conditions | Completed | Preparation failures | Measurements |
|---|---:|---:|---:|---:|
| Primary main | 240 | 209 | 31 | 418,000 |
| Transferred main | 96 | 84 | 12 | 168,000 |
| Additional accuracy checks | 12 | 8 | 4 | 16,000 |
| Total | 348 | 301 | 47 | 602,000 |

There were 305 distinct remote attempts: 301 succeeded and four original failures were recovered by successful replacements. Two reused accuracy references add neither attempts nor measurements. Preparation failures never reached cloud execution. The optional local 80-atom diagnostic was stopped after cloud results became available; its partial progress is not a scientific failure. Unrelated sessions were left untouched.

## 6. Best next step

First correct the reduced model's capacity representation and verify its ideal solutions locally. Then tune penalties and pulse settings on training instances, select settings on separate validation instances, and evaluate once on held-out problems with repeated search and placement seeds. Use Optuna alongside an equal-budget random-search control. Establish simulator accuracy before spending on a larger cloud tuning campaign. The local pilot cost no cloud jobs and took 2.454 seconds; the cost and duration of a future physical tuning study have not been measured.

The evidence supports a **fixed-policy benchmark**, not quantum advantage or a fourteen-atom scaling limit. The textbook method's small-case improvement after changing penalties and controls is direct evidence that configuration matters. Optuna can automate the search; it cannot correct an unsuitable mathematical objective or establish simulator convergence.

### Evidence and graphics

- [Original notebook implementation audit](../REPORT.md), including the earlier documentation and notebook checks.
- [Primary numerical tables](analysis/REPORT.md) and [all final counts and three-gap summaries](analysis/FINAL_METRICS_REVIEW.md).
- [Transferred results and classical controls](analysis/TRANSFERRED_FINAL_INTERPRETATION.md).
- [Per-problem clustering and both routing gaps](analysis/BEST_GAPS.md), [reference and gap figure](plots/reference_and_gaps.png), and [failure-inclusive delivery coverage](analysis/PIPELINE_COVERAGE.md).
- [Simulator comparison methods](analysis/ACCURACY_METHOD.md), [all eight observable checks](analysis/ACCURACY_OBSERVABLES.md), and [independent diagnostic review](analysis/ACCURACY_OBSERVABLES_REVIEW.md).
- [Placement objective and vendor-source review](analysis/EMBEDDING_OBJECTIVE_REVIEW.md), [capacity derivation](analysis/CAPACITY_DEPENDENCE.md), and [Optuna pilot](tuning_pilot/REPORT.md).
- [Provider accounting and timing](cloud_checks/final_accounting/SUMMARY.md).

Provider capabilities and configuration were checked against the [Pasqal cloud integration documentation](https://docs.pasqal.com/cloud/emulators-integration/) and [MPS emulator documentation](https://pasqal-io.github.io/emulators/latest/emu_mps/api/). Recorded local package versions do not establish the provider deployment version.
