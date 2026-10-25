# Placement sensitivity and solution preservation — interim report

**Status: incomplete.** The custom placement study, regulation supplement, and their 100 selected medium-layout checks are complete and independently reviewed. Supplemental bounds now exclude feasible ground states in all 200 completed medium energy systems; two unconstrained minima remain uncertified. The main BLaDE study and its selected medium checks remain outstanding. This report must not be treated as a final comparison between methods.

## What this study tests

The priority is all ten small textbook/slack instances with 14 atoms, all five medium reduced instances with 20 atoms, and all five medium textbook/slack instances with 45 atoms. Each original coefficient set is retained alongside one independently certified alternative. The [frozen main protocol](PROTOCOL.md) and [regulation supplement](REGULATION_PROTOCOL.md) specify 5,400 placement fits. Different starts are repeated trials of the same problem, not additional independent problems.

The central question is whether poor interaction matching comes from incorrect coefficients, penalty choices, local optimization, initialization, or geometric constraints—and whether it actually changes the answer obtained by minimizing the encoded energy.

## Established findings

### Density alone does not explain the failure

The 14-atom textbook target has 46 nonzero pair coefficients out of 91 possible pairs: **50.55%**. Medium reduced targets have **100%** pair density; medium textbook targets have **34.85%**. Every finite-distance physical pair interacts, so physical support density is 100%; thresholding weak interactions gives a descriptive effective density, not missing physical interactions.

The desired distances also impose incompatible planar constraints. For all original and alternative small textbook targets, one seven-atom within-vehicle clique requires a distance Gram matrix of rank six. Exact planar coordinates require a positive-semidefinite matrix of rank at most two. Medium textbook cliques require rank fourteen. An independent alternative construction verified the structural calculation for all forty targets. See [structural results](density_structure.json) and [independent verification](evaluation/density_review.json).

This proves that exact matching of these distances is unavailable in two dimensions. It **does not** quantify the best achievable interaction error, establish that the tested placements are globally best, or imply a general 14-atom hardware ceiling.

### The reported interaction error is not solution-cost error

The geometric diagnostic compares physical pair interactions with the scaled target:

\[
\epsilon=\frac{\lVert U-\alpha J\rVert_2}{\lVert\alpha J\rVert_2},
\]

where the vectors contain unordered pair coefficients. Thus an error of one means the overall pair-coefficient error has the same Euclidean norm as the target pair coefficients. It does not mean every coefficient is wrong by 100%, nor that the original objective value is wrong by 100%. Large coefficients dominate this metric; a small but decisive constraint can be lost while the global metric improves.

The chosen scalar is the least-squares projection of the physical pair vector onto the target direction. For unrounded coordinates,

\[
\alpha=\frac{U^TJ}{J^TJ},\qquad
c=\frac{U^TJ}{\lVert U\rVert_2\lVert J\rVert_2},\qquad
\epsilon^2=c^{-2}-1.
\]

The error is therefore unbounded; values above one are mathematically consistent with this convention. [All 3,200 custom records satisfy this identity](aggregation/scaling_convention.json). Replacing it with a bounded alignment score would preserve per-target layout ordering under this projection convention; it would not repair the physical energy or its solutions. Joint optimization of the physical linear-field scale and geometry is outside this fixed-scale diagnostic.

The target coefficients quantify that imbalance. Averaged across instances, cross-vehicle assignment couplings account for only **0.133%** of the original small textbook target's squared pair norm and **0.0141%** of the original medium textbook target's squared pair norm. These are shares of squared coefficient magnitude, not edge densities. The small certified alternatives raise that share to **27.1%**; the medium textbook alternatives retain approximately **0.0141%** because their assignment and capacity weights are reduced together. This directly shows why a global coefficient-fitting objective gives some logically important terms little weight. The shares were independently reconstructed from the unscaled target arrays; see [verification](aggregation/component_review.json).

The medium textbook alternative keeps the two penalty weights equal. It therefore does not test independent rebalancing of assignment versus capacity penalties; that tuning question remains open.

For the original compact-start SLSQP best-of-twenty layouts, assignment-group relative errors average **0.966** on small textbook and **0.981** on medium textbook instances. These describe one completed placement arm, not all methods. [Component summaries](aggregation/component_summary.json) retain every complete method/family cohort and verify that the coefficient groups partition both target norm and residual error.

To test solution preservation, the evaluator minimizes

\[
E_{\rm distorted}(z)=\alpha\sum_i h_i z_i+\sum_{i<j}U_{ij}z_i z_j
\]

and checks every tied minimizing bit string against the original assignment, capacity, and objective. This first comparison holds the intended individual linear fields fixed to isolate pair distortion. Actual shared-control endpoint fields are a separate test whenever full sequence construction succeeds. Neither static test predicts quantum sampling rates.

### Custom optimization is complete; more starts do not remove the problem

All **3,200** custom fits finished in **674.83 seconds** of measured wall time, with zero execution exceptions. Independent verification covered all coefficients, positions, saved hashes, reconstructed scales and errors, all 1,600 matched-start groups, and twenty unique starts per arm. There were no reconstruction or occupied-validity disagreements. Optimization stopping failures remain in the results; zero exceptions is not a claim that every optimizer converged.

The following comparison uses the same compact initialization family and the lowest-error occupied-valid result among twenty fixed seeds for each instance. It then averages across ten small or five medium instances. Both algorithms use the same objective and gradient; equal iteration caps do not imply equal runtime.

| Formulation | Target parameters | L-BFGS-B mean error | SLSQP mean error |
|---|---|---:|---:|
| Small textbook, 14 atoms | Original | 0.635 | 0.590 |
| Small textbook, 14 atoms | Certified alternative | 0.654 | 0.679 |
| Medium reduced, 20 atoms | Original | 0.921 | 0.794 |
| Medium reduced, 20 atoms | Certified alternative | 0.913 | 0.815 |
| Medium textbook, 45 atoms | Original | 1.449 | 1.454 |
| Medium textbook, 45 atoms | Certified alternative | 1.459 | 1.514 |

These are new matched-budget results, not directly interchangeable with the earlier report's average over different start-selection budgets. The alternate lattice family and the full frozen-prefix curves remain separate in [machine-readable summaries](aggregation/summary.json). [Independent aggregation review](aggregation/review.json) reproduced all 24 custom summary cells, 96 prefix summaries, and 640 selected-record identities. Eleven groups of synthetic checks covered missing and duplicate records, failed fits, evaluation errors, and seed order. Completion now requires exact frozen-design coverage, not merely a matching record count. The rendered custom plots were unchanged after these checks.

A separate [matched-start analysis](paired_analysis/review.md) verifies actual initial coordinates and target inputs before pairing outcomes. Across the four small target/family cells, SLSQP's mean paired error is higher than L-BFGS-B's by **0.052 to 0.097**. Across the eight medium cells it is lower by **0.034 to 0.142**. Each cell first averages seed differences within an instance, then averages across instances. This is average-start behavior, distinct from the best-of-twenty selection in the table. No algorithm dominates every formulation and selection rule.

![Custom placement error across fixed seed prefixes](aggregation/custom_seed_curves.png)

### Parameters can help preserve answers without improving global error

Across both initialization families, selecting the minimum-error layout among forty starts per small instance gives **zero of ten** optimal instances with original parameters for either custom optimizer. The certified alternative gives **three of ten** with SLSQP, despite its mean best interaction error being slightly worse: approximately **0.596 versus 0.571**. These are exact minimum-energy checks, not sampling estimates.

This comparison is diagnostic and reference-informed: the alternative small parameters use known exact answers to maximize the margin separating incorrect states under ideal coefficient limits. They are not a deployable tuning method validated on unseen instances. Medium reduced alternatives use valid-assignment inequalities and exact binary-state verification. Medium textbook alternatives use a conservative sufficient penalty bound, not exhaustive parameter optimization. The original medium reduced collection contains one parameterization whose intended minimum is feasible but suboptimal; its alternative repairs that formulation error.

![Exact solution preservation after geometry-only selection](aggregation/custom_small_solution_curves.png)

The solution-preservation curves keep initialization families separate. The forty-start comparison above pools both families before selection; consequently it can choose a lower-error but incorrect layout over a correct layout found by one family. This occurs with unchanged original targets: SLSQP's twenty lattice starts preserve an optimal minimum in one of ten small instances, but adding its twenty compact starts and selecting by lower interaction error reduces that count to zero. The mismatch is therefore observable without comparing different penalty targets.

Optuna could later search valid parameter ranges and embedding settings, but a trustworthy objective must include feasibility and original objective quality, with held-out instances and fixed seed budgets. Optimizing only the global interaction error is not supported by these results. The present alternatives establish sensitivity; they do not establish optimal tuning.

### How a subsequent Optuna study should be designed

This is a recommendation, not an executed experiment or a change to the frozen study. Optuna is not installed in the experiment environment as checked on October 25, 2026. Its official documentation supports constrained and multi-objective search, but constraint-aware sampling does not guarantee every proposed trial satisfies hard requirements. Therefore problem correctness and device validity must remain explicit rejection gates outside the sampler. See the [Optuna sampler documentation](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html) and [constraint guidance](https://optuna.readthedocs.io/en/stable/faq.html#how-can-i-optimize-a-model-with-some-constraints).

The most informative next parameter experiment is **independent assignment-versus-capacity penalty tuning for medium slack**, because the present alternative keeps those weights equal. Search their ratio and overall scale separately within analytically sufficient correctness bounds, or verify each proposed target against the exact original optimum and infeasible-state bounds. An unresolved correctness check is not a passing trial. For the reduced formulation, independently vary invalid-code and load-balancing weights while explicitly checking original-objective preservation; larger balance weights need not be safer.

Keep target-parameter tuning separate from a fixed-target placement search. For the latter, tune initialization spread, optimizer settings, force regulation, and any proposed weighting of assignment interactions. Include the current settings and a matched-budget random-search control. Changing the loss changes the method and requires a separately recorded study; it must not alter the running baseline.

Rank configurations first by feasibility-preservation frequency over predeclared starts within each instance, averaged equally across instances, then by original objective quality among feasible answers. Distinguish the conservative criterion that all ground states are feasible from the weaker criterion that at least one is feasible. Report interaction error as a diagnostic. Treat unresolved classical minima separately, and inspect all tied minima where possible. Evaluate both ideal individual fields and the actual global-control endpoint: improving pair interactions alone may leave the shared-control restriction unresolved. These are static-energy objectives, not quantum success probabilities.

Freeze a new training/validation/test instance split before searching; the current audited instances have already informed the design and cannot serve as untouched test data. Use common placement seeds during search, independent seeds for confirmation, and identical declared per-trial work budgets; also record actual work, including geometry repair. Equal seed labels do not guarantee identical initial arrays when the target or distance-based initialization changes. Comparisons isolating the optimizer must save and hash identical full starts; comparisons across changed targets should be described as matched-instance comparisons. Report per-instance outcomes and aggregate across instances rather than treating repeated starts as new problems. Freeze the final configuration before evaluating new test instances. Persist proposals, completed outcomes, package versions, and all random seeds. Optuna notes that asynchronous parallel optimization is not exactly reproducible from a sampler seed alone; sequential proposals with parallel, deterministically aggregated inner evaluations are a suitable design here. See its [reproducibility guidance](https://optuna.readthedocs.io/en/stable/faq.html#how-can-i-obtain-reproducible-optimization-results).

### Why reduced-formulation penalties need particular care

The reduced target includes a load-balancing term, not a penalty that vanishes for every capacity-feasible assignment:

\[
E(z)=f(z)+M P_{\rm invalid}(z)+\mu\sum_k(L_k-Q)^2.
\]

For valid assignments, total load is fixed, so

\[
\sum_k(L_k-Q)^2=\sum_k L_k^2-2Q D+KQ^2.
\]

The last two terms are constant, but the first generally differs among feasible assignments. Consequently, raising the balancing weight can change which feasible assignment is preferred by the intended target itself. It is not enough to check capacity feasibility, and simply increasing all penalties is not a general remedy. The exact original-objective checks are essential even before adding placement error. The [target selection review](target_review.md) states the inequalities and exhaustive checks used to certify the tested alternatives.

## What remains running or untested

### Completed regulation supplement

All **200** full-regulation fits completed with zero execution exceptions in **3,190.13 seconds** of measured wall time. Independent verification confirmed the exact target/seed inventory, unchanged frozen hashes, finite final coordinates, five distinct full starts per target, and occupied-geometry validity for every fit. Of these, 139 used 1,200 force updates and 61 required geometry-repair work totaling 1,600 updates. This setting therefore does not guarantee the same amount of work as its default-regulation counterpart.

The complete supplement uses five MDS starts per target. Selecting the lowest-error occupied-valid layout and averaging across instances gives:

| Formulation | Original parameters | Certified alternative |
|---|---:|---:|
| Small textbook, 14 atoms | 1.275 | 1.574 |
| Medium reduced, 20 atoms | 2.459 | 2.562 |
| Medium textbook, 45 atoms | 2.403 | 2.311 |

Exact small-state checks find a feasible optimal minimum for one of ten selected original targets and zero of ten selected alternative targets. Thus full regulation alone does not reliably repair the tested small problems. The matched baseline controls are now complete and independently verified; the paired comparison below supersedes the earlier partial-control status.

### Completed paired five-seed BLaDE comparisons

All **400 paired budget comparisons** and **200 regulation comparisons** are complete. Two reviewers verified exact coverage, full starting-coordinate arrays, target/source hashes, and independent numerical evaluation links. These subsets cover all forty targets, but do not complete the twenty-seed baseline study. The [paired report](paired_analysis/five_seed_complete_report.md) includes all twelve comparison cells and independently recalculated per-instance outcomes.

For each instance, average its five paired seeds, additionally averaging both initialization families for the budget comparison; then weight instances equally. All paired fits are retained, including invalid geometries. These are mean-start diagnostics, **not** best-of-five selection results.

| Formulation and target | Mean error, 200 steps | Mean error, 1,000 steps | Occupied-valid layouts, 200 → 1,000 steps |
|---|---:|---:|---:|
| Small slack, original | 0.509 | 0.504 | 100% → 100% |
| Small slack, alternative | 0.571 | 0.574 | 100% → 100% |
| Medium reduced, original | 0.549 | 0.519 | 100% → 100% |
| Medium reduced, alternative | 0.516 | 0.509 | 100% → 100% |
| Medium slack, original | 1.017 | 0.978 | 52% → 90% |
| Medium slack, alternative | 1.018 | 0.977 | 50% → 94% |

The larger budget uses **6,000 versus 1,200 actual force updates**. Thus longer runs substantially improve medium-slack geometry validity, while mean coefficient matching improves modestly and remains poor. Occupied validity means passing the tested atom separation/radius constraints; it does not establish original-problem feasibility or solution quality.

For small original targets, the instance-averaged fraction of starts whose **all tied minima** preserve the original optimum rises from **1% to 4%**. For certified alternative targets it rises from **28% to 33%**, but four instances improve and four worsen. The corresponding any-tied-minimum rates agree here. These frequencies are neither independent-problem success probabilities nor quantum sampling probabilities. This again shows that the error metric and useful-answer preservation can move differently: alternative small-target error increases slightly despite the average improvement in answer preservation.

Increasing regulation from 0.5 to 1 raises mean interaction error in **all six formulation/target groups**, by approximately **1.048 to 2.616**. On medium slack MDS starts it raises occupied validity from **4% to 100%** for original targets and **0% to 100%** for alternatives, but mean pair errors rise from **0.992 to 2.602** and **0.989 to 2.533**, respectively. On small alternative targets, optimum-preservation frequency falls from **24% to 0%**; on original targets it rises from **0% to 4%**. Stronger regulation is therefore not a general repair.

The regulation comparison includes extra repair work in **61 of 200 fits**: 1,600 updates instead of the baseline's 1,200. Its geometry-validity gain must not be described as a pure equal-work regulation effect. Medium solution preservation is not exhaustively checked for every fit in these paired subsets; the selected-layout endpoint comparisons remain the relevant evidence for that separate claim.

### Completed medium solution checks

All **100 selected custom/regulation layouts** constructed valid complete global-control sequences. Independent review reconstructed interactions from their saved coordinates and re-sampled the serialized sequences. Thus these failures cannot be attributed simply to an inability to construct the tested sequences.

Each layout was tested twice: pair distortion with intended individual fields, and the actual shared-control endpoint. All **200 returned binary witnesses** are infeasible for the original problem, with the stronger ground-state conclusions qualified below.

| Selected placement group | Energy systems | Minimum-energy certification | Systems excluding every feasible ground state |
|---|---:|---|---:|
| Custom, medium reduced | 80 | All 80 exhaustively enumerated | 80 |
| Custom, medium textbook | 80 | All 80 numerically certified | 80, including one supplemental bound |
| Full regulation, medium reduced | 20 | All 20 exhaustively enumerated | 20 |
| Full regulation, medium textbook | 20 | 18 numerical certificates; 2 timeouts | 20, including three supplemental bounds |

The independent reviewer repeated **104,857,600 state-energy evaluations** for all 100 twenty-bit systems. Every one has a unique, infeasible ground state. The 45-bit results use numerical solver certificates rather than exhaustive enumeration; an infeasible returned witness alone is not sufficient to exclude feasible tied minima.

The original fixed-budget custom textbook checks excluded feasible ground states in 79 of 80 energy systems. A separately frozen, single-thread, 60-second-limit bound refinement resolved the remaining case in **18.20 seconds**: the feasible-set lower bound exceeded an independently checked infeasible witness energy by **37.8105**, versus a numerical tolerance of **0.0005534**. The original result was preserved. Three separately recorded regulation refinements also passed independent review, with feasible-set bound separations of **90.2758, 5.3517, and 41.6761**, each above the numerical tolerance. Together, these supplements establish exclusion of feasible ground states in **200 of 200** tested systems. The three regulation refinements used **34.73 seconds** of measured solver time. One retained a time-limit status; its 6.69-second measured duration despite a configured 60-second limit is unexplained. Neither that constrained optimum nor the two original uncertified unconstrained minima is claimed proven. See the [supplemental independent review](selected_validation/regulation_refinement_review.md). See the [independent result review](selected_validation/independent_result_review.md) and [witness/certificate review](selected_validation/INDEPENDENT_REVIEW.md).

### Validation and outstanding work

Pre-launch independent review found and fixed a bug in the **new** medium validator's binary-witness guard: it initially parsed a returned bitstring as a scalar rather than separate bits. No bulk medium result was produced with that bug. The corrected production helper passed a signed 45-bit oracle and invalid-witness rejection checks. Independent full 20-bit tests verified both two-way and 512-way minimum-energy ties; display truncation does not truncate classification. [The claim review](selected_validation/independent_claim_review.md) also checks energy signs, original-objective decoding, timeout handling, and the numerical bound required to exclude feasible minima. The automatic coordinator requires a review marker matching the final source hash before launching.

- Complete all 2,000 main BLaDE fits. All 200 regulation counterparts and 400 budget pairs are already verified. The stronger iteration budget uses five predeclared seeds; baseline uses twenty. Do not extrapolate either to untested seeds.
- Verify every saved start, source hash, geometry and small exact result independently.
- Complete the **80 main BLaDE medium selections** when their full placement arms finish. The 80 custom and 20 regulation selections are already checked. Preserve timeouts and certificates separately.
- Apply full sequence and actual endpoint checks to the remaining BLaDE selections. These checks passed construction and independent reconstruction for the completed 100 layouts.
- Apply the reviewed aggregation to the complete BLaDE and regulation results; finish paired algorithm/budget comparisons, remaining plots and final coverage reconciliation. The BLaDE plotter now covers all thirty comparison groups and has passed [independent review](plot_blade_independent_review.md), including a corrected malformed-input count guard. It refuses incomplete data. Final empirical rendering and visual inspection remain pending.

The [BLaDE audit](blade_review.md) checks the installed implementation against official documentation. Its threshold setting does not hard-delete weak target edges. The separate force-regulation sensitivity arm and all of its paired controls are complete and verified. All current runs are local. No cloud job or cloud spending was required for these static geometry and classical-energy comparisons.

## Current interpretation

The completed custom results do not support the claim that simply adding more random starts or switching between these two local optimizers fixes small textbook or medium embedding. They do support separating target correctness, geometric matching, and preservation of useful answers. The completed paired subsets show that stronger regulation is not a general repair and extra iterations improve medium geometry validity more than coefficient matching. The final twenty-seed method ranking and best tested medium solution conclusions must await the remaining frozen runs.
