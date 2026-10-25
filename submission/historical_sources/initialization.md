# Adaptive initialization diagnostic

Completed 120 of 120 matched fits. No cloud sampling was performed.

The alternative uses feasible triangular-lattice starts with reproducible label permutations, rotations and jitter. Everything after the starting positions is unchanged: objective, analytic gradient, eight restarts, 3,000 iterations per restart, winner selection, physical rescaling and layout construction. This changes starting structure as well as feasibility.

| Tier / encoding | Atoms | Fits | Coupling error: original → lattice | Selected convergence | Valid layouts |
|---|---:|---:|---:|---:|---:|
| Large / Reduced | 45 | 15 | 1.3192 → 1.3756 | 9 → 9 | 15 → 15 |
| Large / Textbook | 80 | 15 | 2.5573 → 2.5742 | 0 → 0 | 0 → 0 |
| Medium / Reduced | 20 | 15 | 1.0247 → 1.0809 | 15 → 15 | 15 → 15 |
| Medium / Textbook | 45 | 15 | 1.5962 → 1.6150 | 10 → 12 | 15 → 15 |
| Small / Reduced | 4 | 30 | 0.2099 → 0.2112 | 30 → 30 | 30 → 30 |
| Small / Textbook | 14 | 30 | 0.6942 → 0.7159 | 30 → 30 | 30 → 30 |

Coupling errors first average placement seeds within each instance, then instances. Lower is better. Selected convergence counts optimizer success flags, not proof of a global optimum. Layout validity uses the unchanged full sequence construction, including empty traps. Fit timing excludes layout construction and is descriptive because machine load differs from the saved original run.

All original 45/80-atom starts violate separation: disjoint radius-2.5 micrometre disks centered in the original square would fit inside a 25 by 25 micrometre square, limiting the count to 31. This geometric fact alone does not prove the cause of final fit failures.

![Matched initialization comparison](comparison.png)

## Interpretation

The feasible initialization does not rescue the custom method at this budget. Group-average coupling error is slightly worse in all six groups; every paired instance-bootstrap interval includes zero. All 120 large-textbook restarts still reach the iteration limit, and none of those 15 fits passes unchanged full-layout construction. Occupied geometry itself is valid for all 120 diagnostic fits. Medium-textbook selected convergence improves from 10 to 12 of 15, without improved average coupling error. The original infeasible starts are a concrete weakness but are not sufficient to explain these failures under this alternative. This does not establish an intrinsic hardware limit or rule out other optimizers, initializations, objectives, or budgets. No quantum performance conclusion follows from geometry alone.
