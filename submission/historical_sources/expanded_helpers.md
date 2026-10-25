# Helper atoms across small, medium, and large instances

Updated 2026-10-25 08:59 AM ET. **37/46 cloud jobs complete; 16/20 primary pairs complete.**

## What was compared

All 20 previously archived instances were frozen before cloud results: ten small slack (14 versus 22 atoms), five medium reduced (20 versus 28), and five large reduced (45 versus 53). Both arms are newly fitted; eight extra atoms are free physical helpers. They are minimized over for the fitting objective and measured, then ignored when decoding the original customer assignment. They are distinct from the capacity slack bits already included in the small encoding.

Each arm used two starts and at most 1,500 optimizer iterations. Selection used training loss only. Original target coefficients, energy conversion, shared final detuning, and the 6-microsecond pulse were fixed within each instance. This matches iteration budgets, not runtime or optimizer evaluations. There was no penalty tuning, pulse tuning, answer repair, feasibility postselection, or outcome-based case selection.

Every primary cloud job uses EMU_MPS, bond dimension 128, a 10 ns time step, precision 1e-8, and 2,000 measurement shots. The prespecified first instance of each size also gets both arms at bond dimension 256 and a 5 ns time step. This is one combined numerical-accuracy check per size, not a complete convergence study.

## Primary quantum results

These are raw feasible probabilities: all 2,000 shots remain in each denominator. A feasible answer assigns each customer exactly once without exceeding any vehicle capacity. Small-instance feasibility is the original task criterion; exact consistency of its capacity slack bits is recorded separately in the machine-readable results.

| Size | Completed pairs | No helpers: mean feasible | Eight helpers: mean feasible | Difference | Observed higher / tied / lower |
|---|---:|---:|---:|---:|---:|
| Small, slack encoding | 10/10 | 6.27% | 0.03% | -6.24 pp | 1 / 7 / 2 |
| Medium, reduced encoding | 5/5 | 15.09% | 19.27% | +4.18 pp | 2 / 1 / 2 |
| Large, reduced encoding | 1/5 | 3.30% | 0.00% | -3.30 pp | 0 / 0 / 1 |

Means weight each completed paired instance equally. Missing or failed jobs are never counted as measured zero probability. Until every pair is complete, these are partial-cohort summaries and may be affected by completion order.

![Paired raw feasible probabilities](paired_feasibility.png)

### Every instance

| Size / instance | No helpers: feasible shots | Eight helpers: feasible shots | No helpers: optimal shots | Eight helpers: optimal shots |
|---|---:|---:|---:|---:|
| S / 2002 (previously studied) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2006 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2012 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2031 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2040 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2042 | 0.05% (1/2000) | 0.00% (0/2000) | 0.05% (1/2000) | 0.00% (0/2000) |
| S / 2060 | 62.65% (1253/2000) | 0.10% (2/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2062 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2063 | 0.00% (0/2000) | 0.20% (4/2000) | 0.00% (0/2000) | 0.20% (4/2000) |
| S / 2073 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2002 (previously studied) | 0.95% (19/2000) | 0.95% (19/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2006 | 51.55% (1031/2000) | 26.90% (538/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2007 | 18.50% (370/2000) | 16.45% (329/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2017 | 2.00% (40/2000) | 4.45% (89/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2018 | 2.45% (49/2000) | 47.60% (952/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| L / 2005 | 3.30% (66/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| L / 2011 | 0.00% (0/2000) | running / queued | 0.00% (0/2000) | running / queued |
| L / 2013 | 0.00% (0/2000) | running / queued | 0.00% (0/2000) | running / queued |
| L / 2015 | running / queued | running / queued | running / queued | running / queued |
| L / 2017 | running / queued | running / queued | running / queued | running / queued |

### Additional instances, excluding the original discovery cases

| Size | Completed new pairs | No helpers: mean feasible | Eight helpers: mean feasible | Paired difference |
|---|---:|---:|---:|---:|
| S | 9/9 | 6.97% | 0.03% | -6.93 pp |
| M | 4/4 | 18.62% | 23.85% | +5.23 pp |
| L | 1/5 | 3.30% | 0.00% | -3.30 pp |

The original small and medium discovery instances are shown separately to avoid presenting repeated tests on them as independent new evidence. All five large instances are new quantum tests in this helper comparison. These are existing retrospective problems, not untouched test data; some had prior baseline simulations outside this helper study.

### Accuracy checks

| Instance | Helpers | Primary feasible | Stronger-settings feasible | Primary optimal | Stronger-settings optimal |
|---|---:|---:|---:|---:|---:|
| S / 2002 | 0 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| S / 2002 | 8 | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2002 | 0 | 0.95% (19/2000) | 1.65% (33/2000) | 0.00% (0/2000) | 0.00% (0/2000) |
| M / 2002 | 8 | 0.95% (19/2000) | running / queued | 0.00% (0/2000) | running / queued |
| L / 2005 | 0 | 3.30% (66/2000) | running / queued | 0.00% (0/2000) | running / queued |
| L / 2005 | 8 | 0.00% (0/2000) | running / queued | 0.00% (0/2000) | running / queued |

Bond dimension and time step change together in these checks. Differences cannot be assigned to one setting. Agreement on one instance does not establish convergence for all instances or all state observables.

## Quality of feasible answers

Feasibility alone does not imply a good clustering. Each completed job records the number of feasible shots, original reference cost, best and median cost, and mean relative objective gap conditional on feasibility. A job with no feasible shots has no conditional-quality estimate. Arm-level conditional-quality means can concern different subsets of instances; their difference is not automatically a paired quality improvement. See `per_job.csv` and `summary.json`.

The relative objective gap is \( (C-C^*)/C^* \). It is different from an energy-fitting error.

Only completed primary jobs with at least one feasible shot are listed below. All zero-success jobs remain in the primary comparisons above.

| Instance | Helpers | Feasible shots | Best cost above optimum | Median cost above optimum | Mean cost above optimum |
|---|---:|---:|---:|---:|---:|
| S / 2042 | 0 | 1 | 0.00% | 0.00% | 0.00% |
| S / 2060 | 0 | 1253 | 0.28% | 27.29% | 19.64% |
| S / 2060 | 8 | 2 | 0.28% | 13.78% | 13.78% |
| S / 2063 | 8 | 4 | 0.00% | 0.00% | 0.00% |
| M / 2002 | 0 | 19 | 52.86% | 96.38% | 96.95% |
| M / 2002 | 8 | 19 | 48.71% | 49.01% | 56.64% |
| M / 2006 | 0 | 1031 | 27.37% | 73.09% | 69.43% |
| M / 2006 | 8 | 538 | 37.49% | 70.98% | 66.29% |
| M / 2007 | 0 | 370 | 57.80% | 83.40% | 78.33% |
| M / 2007 | 8 | 329 | 32.67% | 63.03% | 74.07% |
| M / 2017 | 0 | 40 | 59.66% | 95.04% | 84.31% |
| M / 2017 | 8 | 89 | 44.55% | 87.23% | 74.25% |
| M / 2018 | 0 | 49 | 71.43% | 82.81% | 80.03% |
| M / 2018 | 8 | 952 | 48.74% | 50.32% | 51.91% |
| L / 2005 | 0 | 66 | 149.33% | 212.14% | 210.68% |

## Static fitting and implementation checks

All 80 fitting runs completed; 29 optimizers reported convergence and 51 reached the 1,500-iteration limit. The separate static summary reports whether the lowest physical-energy assignment is feasible or optimal for small and medium. Large-instance static minima are heuristic witnesses, never certified ground states. Low-energy ordering is reported separately from overall energy error.

Independent checks covered exact helper minimization, geometry gradients, all 20 known reference solutions, 1,220 independently scored assignments, 53-bit atom-order permutations, malformed inputs, and six historical cloud result replays. Preparation checks reconstruct interactions and fields from the actual Pulser sequences. Original source and selected models are hashed.

| Size | Mean held-out energy error: no helpers → eight | Feasible lowest-energy answer: no helpers → eight |
|---|---:|---:|
| S (exact) | 0.5756 → 0.3605 | 1/10 → 0/10 |
| M (exact) | 0.3630 → 0.3031 | 1/5 → 0/5 |
| L (heuristic only) | 0.2997 → 0.3060 | 1/5 → 0/5 |

Improved average energy fit does not guarantee preservation of feasible minima. The large low-target-energy holdout correlations average only about 0.037 without helpers and 0.025 with helpers. The mixed-state error hides this poor ordering.

One medium intended QUBO (instance 2007) is already suboptimal for the original clustering objective: its exact optimum costs about 18.02% above the reference. Geometry is therefore not its only source of error. Intended-target optimality has not been certified for the five large instances.

The repeated medium pilot is a fresh refit from serialized starting coordinates. A separate controlled diagnostic restored only the original full-precision starting coordinates and exactly reproduced both archived helper fits, including their final coordinates and losses. Rounding the starts by less than 0.0000005 micrometers was sufficient to change the local optimization paths and which start won the training-loss comparison. The selected physical minimum changed from feasible to infeasible. This demonstrates optimizer-start sensitivity; it does not imply that a fixed final layout requires that placement precision. The frozen expanded study was not changed after this diagnosis.

## Limits and current status

- This cohort is the existing selected benchmark set, not a random sample of all clustering problems.
- There are only five independent medium and five independent large instances. Shot intervals quantify sampling uncertainty within a job; they do not quantify variation across problem instances or simulation bias.
- Exploratory paired-instance bootstrap intervals are saved in the JSON. They resample instances and do not model numerical simulation error. With five instances, population claims remain weak.
- Small uses slack encoding; medium and large use reduced encoding. Cross-size differences combine size and encoding changes.
- Small/medium training uses exact-state information; large training uses sampled uniform states and target-energy local searches. These are diagnostic fits, not a demonstrated scalable production solver.
- Helpers may improve local energy biases as well as pair interactions. A helper benefit alone does not isolate pair-matrix fidelity as the sole cause.
- A fixed eight helpers means a different relative overhead at each size.
- This tests the present free-helper fitting procedure, not every possible redundant encoding.
- Cloud cost is unavailable; no zero-cost claim is made.
- Current cloud state counts: `{"completed": 37, "submitted": 9}`.

## Reproducibility

Frozen inputs and settings: `../manifest.json`, `../protocol.json`, `../quantum/PLAN.json`. Raw counts and per-job metrics: `../quantum/cloud/`. Independent review: `../review/DESIGN_REVIEW.md`. Static results: `../validation/static_summary.md`. Sampled diagonal-energy minima: `../validation/sampled_minima.md`. This report is generated by `../analyze.py`.
