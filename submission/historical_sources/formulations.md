# First-instance formulation search: correctness gate

## What this is

The pulse comparison's original and diagnostic formulations are now supplemented by a frozen parameter menu. This stage tests whether lower or differently weighted penalties still represent the intended constrained clustering problem. It does not choose a winner from interaction error alone.

## What was done

Before new certification, plan.json froze 66 candidates on the first development instance of each family. The menu includes existing original and linear-program alternatives, penalties derived from a capacity-feasible assignment without its optimum, independent assignment/capacity ratios, lower logarithmic grids, and reduced-encoding balance weights with a sufficient assignment penalty that makes removing an invalid duplicate bit lower energy. The latter bound alone does not guarantee capacity feasibility or original optimality.

Coefficient construction is a fresh literal polynomial expansion with no production-builder imports. Independent direct objective and squared-constraint expressions verify each of the three affine coefficient components on all binary states for 14 and 20 bits. Since every candidate is a linear combination of those verified components, each candidate can then be checked by scanning its independent direct energies without repeating all pair multiplications. Six existing original/alternative matrices were independently reconstructed; maximum coefficient difference was 1.17e-10.

## Results

| Family | Candidates | Certified correct | Proven incorrect | Bound insufficient |
|---|---:|---:|---:|---:|
| Small textbook, 14 bits | 26 | 18 | 8 | 0 |
| Medium reduced, 20 bits | 22 | 11 | 11 | 0 |
| Medium textbook, 45 bits | 18 | 6 | 0 | 12 |

The small gate checks all 16,384 states; the medium reduced gate checks all 1,048,576 states. Every lowest-energy state must be feasible and have the original optimal clustering cost. For textbook encoding, helper bits must also satisfy the capacity equations. The maximum direct-versus-polynomial discrepancy across the affine component checks is 1.10e-11.

For 45 bits, the objective is nonnegative and any invalid assignment or capacity equation has an integer residual with square at least one. Therefore its energy is at least the smaller penalty. A valid optimal assignment with exact helper bits has the proven reference cost. A strict penalty above that reference proves every minimum encoding-correct and original-optimal. The transferable stronger version uses the cost of an explicitly found feasible assignment rather than the optimum. Failure of these sufficient bounds is recorded as **uncertified**, not as proof that the formulation is wrong.

Small certification took 0.76 seconds, medium reduced 24.93 seconds, and medium textbook 0.18 seconds. These are measured times. To preserve the single-worker local compute budget, the pulse search was paused for 26.37 seconds and resumed immediately; pulse_pause.json records this. That wall-time pause can appear inside one pulse trial's elapsed timing.

## Issues and gaps

The initial menu certificates cover one development instance per family. The subsequent transfer stage below checks the selected parameter rules across all existing same-family instances. The linear-program alternatives and their neighboring grid are optimum-informed diagnostics, not deployable learned rules. Bound-based witness candidates use no optimum in parameter construction, although the retrospective correctness check uses the exact reference.

A large ideal coefficient gap does not establish an achievable geometric gap or good quantum dynamics. The reported ideal scale uses only individual coefficient bounds; it does not prove that all those coefficients fit simultaneously in a plane. The subsequent bounded placement stage below measures geometric error for this menu.

For example, the small original ideal gap is 0.232 radians per microsecond and the diagnostic alternative is 1.489. These are intended coefficient gaps at their ideal bound-limited scales, not gaps achieved by the chosen atom layouts. For 45 bits the saved bound concerns invalid encodings only; the gap to feasible suboptimal answers is not certified and is intentionally left unknown.

## Current status

Correctness, bounded placement, and selected-rule transfer stages are complete. The separate existing pulse search remains active. No cloud jobs were launched by this stage.

## Best next step

Evaluate the certified transferred targets with matched intended/geometric quantum dynamics, fitting fresh layouts under the same fixed budget where required. Keep evaluation outcomes out of pulse selection. Record invalid transferred models as failures rather than silently dropping them. No claim that better interaction error alone improves solving is justified.


## Bounded placement and transfer results

The frozen placement rule used the same two triangular-lattice starts (seeds 7000 and 7001) and SLSQP iteration limit 1500 for all 35 valid candidates, including original and diagnostic anchors. All 70 attempts produced constraint-valid occupied layouts; 61 reported optimizer convergence and nine did not. No exceptions occurred. Total recorded solver time was 29.89 seconds. A constraint-valid layout is not proof of an optimal placement.

Selection used the nondominated frontier in two quantities: smaller pair interaction error and larger **intended** incorrect-state gap multiplied by the fitted conversion scale. This is not the energy gap of the distorted Hamiltonian. For 45 bits it is only a rigorous lower bound against invalid encodings, not against feasible suboptimal assignments. Original and diagnostic anchors were retained; at most three new frontier rules were added using frozen minimum-error, maximum-gap, and normalized-distance criteria. No quantum probabilities entered this selection.

| Family / representative | Pair error | Intended gap at fitted scale |
|---|---:|---:|
| Small original | 0.909 | 0.125 |
| Small new minimum-error rule | 0.512 | 0.587 |
| Medium reduced original | 0.739 | 0.481 |
| Medium reduced new minimum-error rule | 0.593 | 0.296 |
| Medium reduced new maximum-gap rule | 1.425 | 0.741 |
| Medium textbook original | 1.938 | 0.0410 lower bound |
| Medium textbook new witness rule | 1.711 | 0.0782 lower bound |

The small new minimum-error rule multiplies the diagnostic linear-program assignment penalty by two and leaves its capacity penalty unchanged. The medium reduced table illustrates a genuine tradeoff: improving normalized interaction error can coincide with reducing the intended energy separation. None of these numbers establishes quantum success.

Selected **rules**, rather than their first-instance numeric penalties, were then transferred to all ten small and five medium problems. This produced 90 rule-instance checks: **79 valid and 11 rejected**, with no uncertified cases among the selected rules. Measured transfer certification time was 54.37 seconds.

- Original and diagnostic small anchors pass all ten instances. The new minimum-error small rule also passes all ten. The other two selected small rules fail on one and eight instances respectively.
- Original medium reduced fails one of five instances, consistent with the prior audit. The diagnostic alternative and two new rules pass all five; another new rule fails one.
- All three selected medium textbook rules pass all five instances using the sufficient proof bound.

These failures remain in transferred/manifest.json. Failed transferred models have no approved coefficient artifact for quantum comparison. This is why optimizing penalties on one problem cannot establish a generally correct formulation. Transfer gates use exact reference information retrospectively; they must not be advertised as independent deployment validation. The subsequent equal-budget transferred-layout stage below now supplies these layouts.


## Equal-budget transferred layouts and quantum screen

A diagnostic menu keeps original and linear-program anchors plus new rules that passed correctness on every existing same-family instance: one small textbook rule, two medium reduced rules, and one medium textbook rule. **This menu selection used retrospective correctness across all instances. It is not a fresh held-out evaluation.** The original medium reduced failure remains explicitly excluded as an incorrect model, rather than being repaired or silently omitted.

The menu contains 65 rule-instance cases: 64 certified and one incorrect. All 64 certified targets now have layouts from the same two lattice starts and SLSQP 1500-iteration budget. Of 128 fits, 20 exact matching earlier fits were reused with source and array checks, and 108 were newly run. All 128 satisfy occupied-layout constraints; 114 report optimizer convergence. New solver time totals 44.54 seconds. No certified target lacks a valid layout. Each target's minimum-error valid fit is selected without consulting quantum results. Geometry and raw coefficient artifacts for the medium cases are ready for the separate cloud dynamics stage.

Before quantum outcomes, quantum_screen/pulse_menu.json froze a baseline plus 11 scrambled Sobol points using seed 20261025. All three small formulations and both interaction arms receive exactly the same 12 pulses. Only the first three development instances are evaluated in this pilot, giving 216 coarse full-state evolutions. The objective is mean original-optimal clustering probability, with feasibility and exact helper-bit metrics retained. The three best pulses per formulation/arm are refined at smaller timesteps; each selected pulse is also tested unchanged on the opposite interaction arm. The screen is complete; its checked results and limitations are reported below.

## Later stronger medium-textbook certificate

The initial 12 medium-textbook entries labeled “bound insufficient” were **not** proven wrong. A later independent mixed-integer optimization certificate proves all 12 correct for the first instance. Its weakest common candidate has minimum invalid-state energy at least 478.343765 after a solver-tolerance safety subtraction, above the original optimal cost 438.923297, giving a conservative separation of 39.420468 before physical scaling. Increasing its nonnegative penalties establishes the other candidates' correctness; two additional candidate solves independently agree.

See [the stronger certificates](../medium_slack_certification/monotonic_certificates.json). This supersedes their *current* uncertified status for that first instance, while preserving the original gate results as an honest record of the weaker test. The original 35-candidate fitting design is unchanged. Transfer certificates across all five medium instances are a separate ongoing stage; no quantum success follows from these classical certificates alone.

The weakest quarter-witness medium-textbook rule was subsequently tested across all five instances. It passes three and fails two: the failing minima omit a customer and beat the intended reference by approximately 0.4406 and 0.9710 energy units. See [the transfer evidence](../medium_slack_certification/transfer_all/manifest.json). This again distinguishes a correct first-instance formulation from a transferable rule. A higher assignment penalty with the same reduced capacity penalty is being checked separately; it has not changed either running quantum study.

That assignment refinement is now certified on all five medium-textbook instances: assignment penalty is one half and capacity penalty one quarter of the capacity-only witness cost plus margin. Certified gaps against every invalid state range from 25.55 to 213.09 before physical scaling. [Its five target certificates](../medium_slack_certification/transfer_all/assignment_refinement/manifest.json) are ready for a future quantum comparison. The independent completed review classifies all 90 medium-textbook candidate-instance pairs as 82 valid and eight invalid, with none unresolved. These new certificates do not change the already frozen quantum studies and do not establish quantum success.

## Completed development quantum screen

The screen completed all 216 coarse evolutions and six formulation/interaction-arm selections. The final verifier passed source hashes, metric containment, winner selection, and all finalist and matched-transfer empirical refinement checks. Each final comparison passed successive-distribution total variation below 0.001; this is an empirical absolute convergence check, not a rigorous error bound or certification of tiny-tail relative accuracy. Separate coordinate serialization differences remain outside that integration check.

The following are **three-instance development means**, with each arm choosing its own best pulse for original clustering optimality from the same 12 candidates. Correct helper bits are required only in the full-QUBO-ground column.

| Formulation | Interaction arm | Feasible assignment | Original-optimal assignment | Full intended-QUBO ground state |
|---|---|---:|---:|---:|
| Original | intended | 3.6420% | 1.9542% | 0.136786% |
| Original | geometric | 0.3375% | 0.3367% | 0.000267% |
| LP diagnostic | intended | 91.2615% | 53.9637% | 1.918415% |
| LP diagnostic | geometric | 2.7626% | 1.2056% | 0.001036% |
| New assignment-penalty rule | intended | 87.6338% | 49.4829% | 1.710851% |
| New assignment-penalty rule | geometric | 12.5852% | 5.8758% | 0.449095% |

The intended LP pulse has 53.96% original-optimal assignment probability but only 1.92% full-QUBO-ground probability: many samples get the customer assignment right while their slack bits are wrong. Thus 53.96% is not an exact-QUBO solving rate. Running that same pulse on geometric interactions reduces mean feasible-assignment probability to 0.496% and original-optimal assignment probability to 0.00168%. Its computed ground probabilities are near zero; they must not be reported with relative accuracy or used to claim precise shot-success probabilities without targeted rare-tail validation.

The new penalty rule improves the geometric arm under this limited screen to 5.876% original-optimal assignments and 0.4491% full ground states. Its intended-arm clustering-selected pulse gives 49.48% original-optimal assignments but 1.711% full ground states. Because pulse selection optimized assignments, this comparison does not establish which formulation optimizes full-ground solving. A separately frozen Beta-ramp study now optimizes the full-ground metric directly with 3 independent optimizer seeds and 24 new adaptive trials per formulation/arm, plus 12 cached warmstarts counted separately. All seed winners will be retained and evaluated on both arms.

These formulations were selected with correctness information from every existing instance; subsequent pulse-held-out cases are conditional on that retrospective model selection. Twelve fixed pulses and two placement starts do not establish the best possible hardware embedding or pulse. No fundamental scaling limit follows from this screen.
