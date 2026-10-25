# Redundant-atom static results

All 27 layouts passed the independent algebra check. All 84 serialized simulation conditions passed the independent device, geometry, intended-matrix and sampled-control checks. All 27 saved static case hashes match the finalized case files. All 9 original constrained reference values were independently reproduced. Six original slack targets passed an independent polynomial reconstruction and sufficient-penalty proof; three reduced targets had every original minimum exhaustively enumerated and decoded correctly.

The table reports centered energy error divided by the standard deviation of intended energy. Lower is better. Only a mean additive offset is removed; no rescaling is fitted. Every auxiliary configuration is minimized exactly with all physical tails retained. Physical fields are sampled after sequence serialization. Zero, two and four denote the number of additional atoms.

| Problem and encoding | Logical-domain error, 0 | Logical-domain error, 2 | Logical-domain error, 4 | Assignment-domain error, 0 | Assignment-domain error, 2 | Assignment-domain error, 4 |
|---|---:|---:|---:|---:|---:|---:|
| M_2002_reduced | 0.8306 | 1.0677 | 1.0872 | 2.526 | 2.580 | 3.135 |
| M_2002_slack | 0.6647 | 0.6907 | 0.7428 | 2131.731 | 2098.502 | 2152.659 |
| M_2006_reduced | 0.7251 | 0.8516 | 1.0941 | 2.586 | 2.491 | 3.043 |
| M_2006_slack | 0.7365 | 0.7590 | 0.8485 | 2363.932 | 2437.078 | 2660.677 |
| M_2007_reduced | 0.8181 | 0.9007 | 1.1317 | 2.298 | 2.428 | 3.039 |
| M_2007_slack | 0.8534 | 0.8566 | 0.8398 | 2010.724 | 1935.133 | 2179.084 |
| S_2002_slack | 0.6464 | 0.6036 | 0.7706 | 246.877 | 258.010 | 190.396 |
| S_2006_slack | 0.5642 | 0.6655 | 0.6348 | 99.281 | 162.987 | 158.537 |
| S_2012_slack | 0.6643 | 0.8374 | 0.7452 | 94.492 | 56.680 | 56.781 |

Only 2 of 18 augmented layouts improve the logical-domain error against their own zero-auxiliary baseline. All three medium reduced problems worsen monotonically with two and four added atoms. Assignment-domain error improves in 6 of 18 comparisons, showing that full-domain and solution-domain fidelity can disagree.

Logical-domain results are exhaustive over all 16,384 original bitstrings for small slack and all 1,048,576 original bitstrings for medium reduced. Medium slack uses the same 4,096 fixed random original bitstrings at each redundancy level; this is a sample, not a global proof. Assignment-domain results enumerate all 59,049 valid reduced customer assignments, including capacity violations, or all capacity-feasible customer assignments with canonical clipped-weight slack. Small slack has only four such assignments for each problem. These domains are distinct and must not be pooled. Very large slack assignment-domain errors reflect large penalty-induced distortions relative to the much smaller spread in feasible clustering costs.

Every physical endpoint solve established an optimal energy. For systems through 20 total atoms, every tied minimum was enumerated. For larger systems, only one optimizer-returned minimum was decoded; equal-energy feasible minima have not been excluded. One physical minimum was feasible but clustering-suboptimal: the zero-auxiliary medium reduced problem with seed 2007. The checked physical minima for the other 26 layouts were infeasible. None of the returned or fully enumerated physical minima attained the original clustering optimum. This is not an all-ties infeasibility or nonoptimality certificate for larger systems. The bounded original 45-atom optimizations can time out; original-target correctness is instead established by the independent slack proof.

All 27 serialized local-field error spans are below the corresponding incorrect-state gap bound (including the wire excitation bound). This preserves correct-versus-incorrect intended endpoint separation, but intended ties can split. Rounded coordinates, six-decimal pair distances and six-decimal detuning weights match the checked simulator conventions.

The sparse two-atom wire is algebraically exact after conditional minimization, but this pilot does not show a generally successful fidelity-improving intervention. The chosen selective wire/layout recipe worsens most metrics. Its emulations can characterize that recipe and the dynamical burden of auxiliary atoms; they cannot establish that improving embedding fidelity improves performance unless a tested condition actually improves the relevant fidelity. Three problems per family remain a pilot, not a broad representativeness claim.

Independent inspection and static analysis only; no cloud jobs were launched by the verification role. Production measurements are not included in this static summary.
