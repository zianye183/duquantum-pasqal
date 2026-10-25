# Track A research milestone: compact encoding, no practical advantage

The four-atom prototype is a useful compact implementation of the two-vehicle problem, but a cheap balanced random-assignment control performs better. The earlier eight-atom pilot did not generalize. These are verified local emulator results, not QPU measurements or evidence of quantum advantage.

## Main comparison: 100 fresh tier-S instances

| Method | Mean feasible probability | Mean original clustering-optimum probability |
|---|---:|---:|
| Four-atom physical emulator | 72.85% | 19.38% |
| Uniform vehicle assignment | 62.63% | 12.50% |
| Uniform two-customers-per-vehicle assignment | **91.33%** | **32.33%** |
| Physical excitation counts, spatial preferences erased | 71.38% | 16.50% |

The physical method beat unrestricted uniform assignment on 99 instances and lost on one. It beat balanced assignment on only four and lost on 96. Balanced assignment samples uniformly among six labeled two-versus-two splits; it does not inspect coordinates, optimize costs, or repair capacity failures. It is not a general capacity solver, and can miss one-versus-three optima.

The two stronger controls were added **after execution by an independent critic**, so they are explicitly post-hoc analyses. The final row preserves the physical distribution's probability of each excitation count, then erases spatial preference within each count. It uses physical output and is a diagnostic, not an independent classical sampler. Its difference from physical performance suggests an average spatial contribution of 2.87 percentage points in optimum probability, insufficient to beat the simple balanced heuristic.

Primary metrics above are sums of numerical final-state probabilities, not finite-shot estimates. The experiment additionally stores 2000 measured samples per instance. All sampled runs reached the model optimum, but the selected clustering's mean routed-CVRP gap was 4.718%. This illustrates why a zero best clustering gap does not imply optimal vehicle routing.

## What was tested

- Three development instances with a fourteen-atom textbook slack formulation, an eight-atom soft capacity surrogate, and a four-atom two-vehicle reduction.
- A frozen twenty-instance eight-atom validation: feasibility 26.40% versus 62.50% for uniform assignments; optimum probability 6.45% versus 12.50%. Nineteen selected geometry fits stopped without optimizer success, although their outputs were physically legal. No failures were dropped.
- A frozen hundred-instance four-atom validation: the first hundred feasible original draws starting at seed 4000. Three infeasible initial draws were rejected before simulation; no outcome-based seed substitution occurred. All hundred simulations and selected geometry fits succeeded. Only twelve instances had active capacity constraints.
- A separate 256-instance mathematical audit with 1536 fixed-weight comparisons. Increasing the soft capacity penalty improves feasibility but can destroy the original distance optimum.
- Independent direct constrained CPLEX checks for clustering and full CVRP on all 123 unique small-tier physical-study instances: **246/246 solves matched exhaustive references**. Maximum absolute disagreement was below \(2.90\times10^{-12}\).

The original logical slack formulation uses fourteen atoms on tier S. The four-atom representation removes both six slack bits and four redundant assignment bits: a 71.4% reduction. It represents assignment exactly for two vehicles, but retains a soft capacity objective and approximates unequal fields through global detuning. This is not an exact four-atom encoding of all CVRP constraints.

## Why the models fail

The global-detuning device cannot independently reproduce unequal linear coefficients. Even positive pair coefficients may not admit the requested two-dimensional distances. The textbook formulation has exact logical penalties, yet every pilot's fitted physical minimum violates constraints.

Eliminating capacity slack with identical quadratic penalties changes capacity enforcement into load balancing. Under exactly-once assignment,

\[
\sum_k\left[a(L_k-Q)+b(L_k-Q)^2\right]=b\sum_kL_k^2+\text{constant}.
\]

The common linear asymmetry and the capacity threshold no longer affect rankings in this subspace. This derivation was independently checked. It explains why a method advertised as an inequality penalty cannot simply be assumed to enforce capacity here.

The four-atom reduction preserves the chosen abstract two-group surrogate, with positive pairs and unequal fields. Its physical approximation can either improve or worsen feasibility by accident. Eleven validation instances had physical ground-state sets containing capacity violations. Slower preparation is therefore not automatically better.

## Verification and limits

An independent critic inspected code and artifacts, reconstructed probability masks and couplings, reproduced seed selection, checked bit order with synthetic basis states, reran direct CPLEX solves, and performed additional emulator refinements. The three four-atom development runs changed by total variation below \(4.6\times10^{-5}\) when the integration step was halved. The prespecified first four-atom validation instance changed by about \(4.06\times10^{-5}\). These are bounded numerical checks, not convergence certification for every instance.

Every experiment used actual AnalogDevice geometry and four-microsecond global pulses. There were no programmable interaction overrides, local-field DMM substitutions, hidden repair, paid cloud calls, or hardware execution. Simulations were noiseless and omitted finite-bandwidth modulation. Exact references and geometry fitting are classical work; no runtime speedup is claimed.

The small-tier validation remains the only larger sample of instances. A separate four-instance medium/large pilot below tests an explicit recursive extension. Noisy/modulated pulses, stronger classical optimizers, and large-node numerical convergence remain untested. Four-atom encoding directly applies to two vehicles; recursive extension changes the surrogate objective.

## Reviewed medium/large recursive pilot

A frozen recursive extension used ten atoms for ten-customer, three-vehicle instances and fifteen atoms for fifteen-customer, four-vehicle instances. Each instance received sixteen complete trajectories. Internal splits were never repaired or conditioned on feasibility. Empty branches represent unused vehicles.

| Instance | Physical feasible | Balanced random feasible | Best physical clustering gap | Route gap of that same output |
|---|---:|---:|---:|---:|
| Medium first | 0/16 | 5/16 | undefined | undefined |
| Medium second | 6/16 | 11/16 | 110.28% | 35.25% |
| Large first | 0/16 | 7/16 | undefined | undefined |
| Large second | 1/16 | 16/16 | 177.45% | 79.46% |

The physical method returned **7/64 feasible trajectories**, compared with **39/64** for prespecified proportional-cardinality random splitting. A single demand-first greedy assignment was feasible on all four instances; its budget differs from the sampled controls. No sampled method reached the clustering optimum. These are pilot frequencies, not exact final-output probabilities; zero successes in sixteen trials does not establish zero probability.

The recursive objective charges pairs at ancestors even when they separate later. Its squared load terms favor balance rather than enforce capacity. Averaged fields additionally lose individual demand information. One intended root minimum already violates aggregate child capacity; on the other three instances intended minima pass that necessary test but realized physical minima fail it. Root pair errors range from 66.7% to 79.5%. Passing aggregate capacity does not establish descendant packability.

Resource accounting totals **159 physical measurement calls**, **1,375 atom-preparations**, and **86 distinct cached emulations**. Every traversal samples afresh. One selected geometry fit did not converge; its legal output remained in the experiment. Four measured pipeline runtimes total about 68.8 seconds, excluding serialization and later evaluation. No hardware timing claim follows.

Exact subset enumeration with dynamic programming establishes all four clustering and full-routing references, allowing unused vehicles and counting unlabeled model optima. All eight independent CPLEX incumbents agree; seven were proven by CPLEX, while one routing solve reached its 30-second limit with a 0.689636% solver gap. Its optimum is separately proven by the exhaustive recurrence. Reference calculations never supply optimizer decisions.

An independent critic ran twelve tests, reconstructed all saved node geometries/interactions/energies, checked every sampled partition and feasible routed cost, and independently checked reference witnesses. Halving the integration step for one medium root changed its distribution by total variation 0.0001536. This does not certify large-node convergence. Preserve this failed pilot before changing the formulation; more shots alone cannot fix the demonstrated objective and geometry failures.

## Reproduction and records

With the pinned environment installed, verify saved evidence and recompute the stronger controls:

```sh
python research/track_a/reproduce.py
```

Rerun simulations and direct reference checks in a separate output tree, preserving the original frozen records:

```sh
python research/track_a/reproduce.py --simulate
```

The repository contains complete seeds, certificates, geometries, serialized sequences, raw samples, exact numerical state probabilities, solver settings, results tables and independent-review notes. Separate exploration branches retain their logical commits; the integration branch preserves their merge history. The original checkout's notebook edits were not modified or committed by this research session.

## Decision

Keep the four-atom implementation as a compact, explainable Track A demonstrator. Reject any headline of practical superiority. The recursive larger-tier extension also failed its simple balanced control. Diagnose logical and physical losses separately before pulse tuning or a fresh formulation. Any new method needs a fresh test set; both validation cohorts are now inspected data.

AI disclosure: Codex agents wrote the prototype code, derivations and documentation, ran experiments, and independently criticized the results. These checks do not replace the challenge's requirement that team members understand and defend every submitted model and claim.
