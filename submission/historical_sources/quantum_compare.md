# Quantum solving audit — interim report

**Status: incomplete. This is a living research report, not a completed benchmark.**

## Current verified findings — October 25, 2026, 7:36 am ET

The small-slack study is complete and independently reviewed: **944 fresh trials, 34 retained winners, and 680 case/interaction evaluations**. When trained for complete solutions with exact interactions, the alternative formulation achieves **11.8–23.7% mean complete-optimum probability** across three optimizer seeds, versus **1.33–2.26%** for the original formulation. Applying those same selected pulses to geometric interactions gives means below the 0.1% reporting floor. Separate training on geometric interactions reaches at most 0.168% mean complete-optimum probability in this study. Five retrospective evaluation instances, oracle-informed formulation construction, finite tuning budgets, and idealized controls limit generalization. [Completed small study](small_results/REPORT.md), [independent review](full_medium_review/SMALL_FINAL_REVIEW.md).

All four fixed-pulse 20-atom reference simulations are complete and independently verified. Fine-reference feasible probabilities are **36.7942% with exact interactions and 3.8912% with geometric interactions**. Halving the timestep changes each by less than 0.0004 percentage points. Frozen grouped cloud-distribution checks detect no broad discrepancy at their declared threshold; documented rare-category discrepancies remain. This covers one instance and one pulse, not tuned medium-scale performance. [Reference evidence](local20_reference/REPORT.md).

The classical audit of the actual operational inputs on one development instance is complete. All six intended endpoint models retain correct optimal ground states; all six geometric models exclude every originally feasible ground state. Twenty-variable models were enumerated, while the 45-variable conclusions combine completed bounded solves and separate correctness certificates. Timed-out optimizations remain explicitly unresolved. [Endpoint audit](medium_endpoint_audit/REPORT.md).

**Still incomplete:** medium-scale tuning, selected-candidate evaluation, and 45-atom numerical refinement. The frozen development study has 28 collected results out of 600 logical runs. Another session's deliberate priority controller currently suspends this study's submission and polling processes; automatic release is configured after its priority study finishes. This is a scheduling hold, not evidence of cloud solver failure. Unlimited emulator access was confirmed, but dollar billing is not exposed. Later sections retain historical experiment details; this section states the current completion status.

## What this study asks

Does replacing the intended QUBO pair interactions with realizable geometric interactions change solving performance? Can pulse and formulation tuning compensate? The required scope is small slack (14 atoms), medium reduced (20), and medium slack (45). The comparison must separate formulation correctness, quantum preparation, numerical error, and cloud execution failures.

An exact QUBO Hamiltonian is not an automatic exact optimizer. If its ground states are feasible and quantum evolution prepares one, the answer is feasible. A finite pulse can instead produce excited states. Geometric error can change both the final energy ordering and the path taken by the quantum evolution.

## Relationship to the completed classical comparison

The earlier [classical endpoint audit](../fidelity/classical_compare/REPORT.md) already proved that pair distortion can move the minimum to an infeasible answer on its saved small-slack and medium layouts. Those layouts differ from the current equal-budget retuned-formulation inputs. Its conclusions therefore provide motivation, not a certificate for these new geometries.

A bounded classical endpoint audit of the actual new serialized inputs is complete; see the current findings above. Quantum runs are retained regardless of endpoint results: finite-time evolution can produce feasible excited states even when the distorted ground state is infeasible. Static correctness and pulse performance must both be measured.

## Success metrics must remain separate

- **Feasible clustering:** every customer is assigned once and vehicle capacities are respected, regardless of auxiliary bits.
- **Optimal clustering:** feasible clustering with the independently known best original objective, regardless of auxiliary bits.
- **Full encoding feasible:** the clustering is feasible and auxiliary slack bits correctly represent remaining capacities.
- **Full intended-QUBO ground configuration:** original-optimal clustering with correct auxiliary bits, for a certified ideal target formulation. This scores the desired target ground-state set; it does not claim that every counted configuration remains an exactly tied minimum after serialized control rounding or geometric distortion.

Actual serialized detuning-map weights can lift ties between symmetry-equivalent intended solutions. The new endpoint audit already finds two actual rounded minima where the ideal target certificate has six; the observed minima remain correct. This distinction affects the meaning of “ground” and is being quantified, without changing the desired-solution scoring.

Counting optimal clusterings as full-QUBO ground-state success would overstate results. A promising development pulse produced roughly 54% optimal clusterings but only roughly 1.9% complete QUBO ground configurations. Those are development readouts from a different equal-budget layout study; they are not the baseline table below. The existing clustering-oriented search remains useful, and a separate complete-QUBO-ground objective search has now completed; its final results are linked above.

All raw outputs remain in the denominator. No repaired or postselected rates are presented as raw success rates. Shot confidence intervals do not cover numerical approximation or variation between problems.

## Verified local baseline: one small slack problem

Four full-duration runs of the official state-vector emulator completed successfully. This rules out a 14-atom emulation barrier in this environment. The table uses full-state probabilities, not estimated shot rates. Pulse duration is 4 microseconds, with the original untuned pulse. Default 10-nanosecond time integration has not yet been certified against a tighter reference for every row.

| Formulation | Pair interactions | Feasible clustering | Optimal clustering | Full encoding feasible | Full QUBO ground configuration |
|---|---|---:|---:|---:|---:|
| original | intended | 5.7580% | 2.6894% | 1.3858% | 0.7065% |
| original | geometric | 1.0361% | 0.7993% | 0.2404% | 0.2319% |
| alternative | intended | 18.1733% | 6.2159% | 0.1399% | 0.0402% |
| alternative | geometric | 3.2461% | 3.1533% | 0.1904% | 0.1799% |

The direction depends on the metric: the alternative improves clustering feasibility here, but its intended full-QUBO ground probability is lower. On that alternative, geometric interactions actually increase full-QUBO ground probability for this particular untuned pulse. Therefore neither matrix error alone nor one feasibility column supports a universal claim about solving quality. Formulation comparisons also include the resulting placement and common energy conversion; they are not isolated changes to one coefficient.

This is one problem, not an aggregate conclusion. See [official local evidence](baseline_local14/summary.json). The independent reference extraction initially complemented occupation bits incorrectly; this was caught using single-excitation and sampled-outcome checks and corrected before the probabilities above were reported. Raw sampled outcomes were unaffected. [Independent review](INDEPENDENT_REVIEW.md).

## Tuning and formulation correctness

The initial formulation menu contained 66 candidates on one development case per family: 35 certified, 19 incorrect, and 12 initially uncertified. Independent mixed-integer optimization subsequently certified all 12 unresolved medium-slack candidates for that first problem. Uncertified did not mean incorrect.

Transferring a promising rule can fail. The weakest medium-slack assignment rule made customer omission preferable on two of five cases. Raising the assignment penalty while retaining the weaker capacity penalty produced a rule certified on all five saved medium problems. Across all 90 medium-slack rule/problem combinations, the later certificate analysis classifies 82 as correct and eight as incorrect. This is retrospective certification on known benchmarks, not a universal guarantee for unseen instances.

The newly certified weaker 45-atom rule has now received ten placement attempts across five problems. All ten placements are physically valid, but six attempts reached the 1,500-iteration limit. Selected relative pair errors range from 1.649 to 2.129 (mean 1.849). These results do not show that weakening valid penalties automatically makes embedding accurate; they also do not establish the best attainable geometry or quantum solution quality. [Placement evidence](medium_slack_certification/newrule_layouts/manifest.json).

An equal-budget comparison gives a more specific answer to whether penalties help embedding. For the five medium reduced problems, the newly selected rule, which doubles the LP assignment penalty while retaining its capacity coefficient, lowers mean pair error from 0.750 for the LP alternative to 0.579, improving every case. For medium slack, corresponding means are 1.857 and 1.849: no consistent improvement across cases. This comparison is retrospective and has only two placement starts per case; it does not yet establish a solving advantage. The original reduced mean uses only four correctness-passing cases and is deliberately excluded from this paired five-case claim. [Per-case comparisons](medium_search/formulation_geometry_comparison.json), [independent norm recomputation](medium_search/geometry_metric_check.json).

Selected original, optimized, and new formulation rules receive equal placement-search budgets within the formulation study. Every attempted fit is retained; a valid final layout does not imply the optimizer declared convergence. The placement tradeoff uses the **intended target gap at the fitted scale**, not the actual geometric Hamiltonian's gap.

Current pulse studies include independently seeded Optuna and random-search runs, a fixed shared pulse menu across formulations, and a separately frozen full-QUBO-ground objective stage. Development, validation, and evaluation cases are separated for pulse selection, but all saved instances were examined previously and formulation correctness selection uses their certificates. None are claimed to be untouched prospective tests.

[Protocol](PROTOCOL.md), [formulation search](formulation_search/REPORT.md), [medium certificate evidence](medium_slack_certification/complete_rule_certificates.json).

## Cloud execution recovered for the original 14-atom pair

Both actual original-formulation baseline jobs completed remotely after replacing sampled linear detuning waveforms with compact linear ramps. Independently checked controls differ by at most \(2.84\times10^{-14}\) radians per microsecond. This changes the representation, not the intended experiment. The remote implementation defect remains unknown. Earlier size, aggregate-detuning, and duration hypotheses do not explain why this same physical experiment now succeeds.

| Interactions | Shots | Feasible clustering | Optimal clustering | Full encoding feasible | Full QUBO ground configuration |
|---|---:|---:|---:|---:|---:|
| intended | 20,000 | 1,141 (5.705%) | 538 (2.690%) | 278 (1.390%) | 132 (0.660%) |
| geometric | 20,000 | 205 (1.025%) | 162 (0.810%) | 42 (0.210%) | 41 (0.205%) |

All eight local full-state reference probabilities lie within the corresponding marginal 95% Wilson shot intervals. This is agreement with the reference, not certification of its integration accuracy or a simultaneous statistical test. These results demonstrate feasible and optimal outcomes for exact-QUBO emulation on one problem, and a reduction under geometric interactions for this pulse. They do not establish medium-size performance or tuned performance. [Scored raw cloud evidence](ramp14_score.json), [local comparison and intervals](ramp14_local_comparison.json).

The remaining ten baseline jobs completed using the same independently checked compact representation. A separate [36-run operational gate](medium_search/operational_addendum.json) now includes original, alternative, and retuned formulations with equal placement budgets. It tests short and long nonlinear pulses before broader medium tuning; the waveform and runtime gates passed, and execution is released. Both complete-ground and clustering objectives will be scored separately. Medium tuned execution and numerical convergence remain outstanding. All failed diagnostic jobs are retained and excluded from solution-quality tables. Uniform energy/time rescaling reproduced the original local evolution but did not resolve cloud execution; it is not used as a substitute for this recovered baseline.

Cloud pricing and charges are not exposed by the inspected SDK. Failed jobs are not assumed free.

## Medium cloud baseline: completed, numerical refinement pending

All four 20-atom reduced and four 45-atom slack baseline runs completed on one medium instance. Each used 20,000 raw shots and the original four-microsecond pulse. These are historical-best placements, distinct from the equal-budget retuned-formulation pilot.

| Encoding | Formulation | Interactions | Feasible assignments | Optimal assignments |
|---|---|---|---:|---:|
| reduced, 20 atoms | original | intended | 7,405 (37.025%) | 131 (0.655%) |
| reduced, 20 atoms | original | geometric | 804 (4.020%) | 2 (0.010%) |
| reduced, 20 atoms | alternative | intended | 8,793 (43.965%) | 105 (0.525%) |
| reduced, 20 atoms | alternative | geometric | 61 (0.305%) | 0 |
| slack, 45 atoms | original | intended | 2 (0.010%) | 0 |
| slack, 45 atoms | original | geometric | 0 | 0 |
| slack, 45 atoms | alternative | intended | 2 (0.010%) | 0 |
| slack, 45 atoms | alternative | geometric | 0 | 0 |

For zero successes in 20,000 samples, the marginal 95% Wilson upper bound is approximately 0.0192%, not zero probability. In reduced encoding, complete-ground and optimal-assignment counts coincide because there are no slack bits. No complete-ground states were observed in the four slack runs.

The 45-atom tensor approximation is **not yet converged**. Three logs reached the exploratory bond-dimension cap of 64; a low observed success rate must not be attributed solely to encoding or pulse quality until refinement passes. Higher-bond and finer-timestep runs are now authorized separately. [Raw scored evidence](ramp_remaining_score.json).

Actual service execution took 900–998 seconds for the 20-atom jobs and 341–400 seconds for the 45-atom approximate jobs. Queue delays for the 20-atom jobs were only 4–12 seconds. Later result-observation times include large local monitoring gaps and are not computation durations. A matching official local 20-atom intended run took approximately 891 seconds of recorded propagation and produced feasible probability 36.7946% and optimal probability 0.6613%, both consistent with the corresponding cloud shot intervals. The previously faster local timing used a different split-operator method and was not an equivalent runtime comparison. The matching geometric local reference completed in 569.76 seconds, with feasible probability 3.8913% and optimal probability 0.0011465%. The intended five-nanosecond reference is complete: distribution total variation from ten-nanosecond integration is 0.000036006, feasible probability changes by about 0.00000379 and optimal probability by 0.000000248. The geometric five-nanosecond reference is now complete, with total variation 0.0000247899 from its ten-nanosecond counterpart; the earlier timeout is retained. A separate assignment-validity diagnostic does not fall inside its marginal cloud shot interval, and the finer timestep does not remove it: two invalid assignments were observed where the local distribution predicts about 0.184. Under that fixed distribution, observing at least two has probability about 1.49%. This is retained as an unresolved rare-event discrepancy, not erased by selective resampling or taken alone as proof of a backend bug. The geometric cloud run also returned two optimal assignments versus approximately 0.229 expected from its local reference; this second rare-rate discrepancy is retained. The affected bitstrings and refined local calculations have been checked; the rare-category discrepancies remain documented without a backend-failure claim. [All local/cloud diagnostic comparisons](medium_search/local_cloud_reference_comparison.json).

All four short/long nonlinear cloud probes also completed and agree with independent local state probabilities under finite-shot multinomial checks (Monte Carlo tail probabilities 0.137, 0.602, 0.922, and 0.499). [Distribution check](nonlinear_independent_review/cloud_compare.json). The reviewed 36-run operational experiment has been released, with a concurrency cap of four. This remains a pilot, not sufficient tuning or completion of the full goal. Cloud charges remain unavailable.

## Nonlinear pulse conversion and review finding

Four independent small-system simulations checked the compact nonlinear pulse representation. Observed probability-distribution differences were below \(1.3\times10^{-8}\). All 36 prepared medium inputs also pass independent input correspondence and true midpoint-grid error checks, with a maximum state-distance bound below \(7.0\times10^{-5}\). This bound compares the two sampled control Hamiltonians; it does not certify numerical propagation or tensor truncation.

The review found a real acceptance-check bug: odd integration steps were evaluated at floored integer sample positions rather than the backend's half-nanosecond interpolation midpoints. Independent true-grid calculations show that existing prepared inputs remain within tolerance. The generic acceptance check is corrected and independently regression-tested. An adversarial pulse passed the old check with a claimed bound of 0.00007838 while its true bound was 0.00012162, exceeding the 0.0001 threshold. The corrected check rejected that representation and refined it to a true bound of 0.00006005. [Regression evidence](nonlinear_independent_review/regression_results.json). Existing frozen inputs are preserved. [Independent review and evidence](nonlinear_independent_review/REVIEW.md).

## Independent check of one very small probability

For one development problem and its fixed analytic pulse, independent adaptive integration reproduces the geometric model's full-ground probability near \(3.81\times10^{-13}\). Tightening the independent solver tolerance changes the raw probability by approximately \(5.6\times10^{-8}\) relatively, or \(3.1\times10^{-7}\) after accounting for the recorded norm drift. Three decreasing split-operator timesteps approach that reference, with the finest differing by about 0.017% relatively. Serializing register coordinates changes the reference probability by about 0.000415% relatively.

This is evidence that this particular tiny probability is reproducible in the analytic model, rather than an inference from a loose whole-distribution tolerance. It is not a rigorous probability bound, does not validate other tiny tails, and does not include sampled nonlinear cloud waveforms or hardware errors. The intended-arm independent matched reference is now complete. [Independent numerical evidence](tail_validation/results.json).

## Matched independent reference: embedding can materially impair solving

A tight independent solver evaluated the same 11.094-microsecond analytic pulse on intended and geometric interactions for one alternative-formulation small slack development case. The pulse was selected for intended-arm clustering performance, not for the geometric arm. Its duration exceeds the real-device limit, so this is an emulator diagnostic.

| Metric | Intended interactions | Geometric interactions |
|---|---:|---:|
| Feasible assignment | 85.2906% | 1.4789% |
| Optimal original assignment | 46.9318% | 0.0001115% |
| Full encoding feasible | 1.3351% | 0.00002159% |
| Complete ground configuration | 0.8604% | approximately \(3.81\times10^{-13}\) probability |

The table distinguishes percentages from the explicitly labeled tiny probability. Raw norm drift was below \(3\times10^{-9}\); normalized scores and raw drift are both retained. The intended complete-ground probability differs from the earlier split-operator screen by about 0.000007 absolute, showing why a whole-distribution gate does not imply all reported digits are accurate.

This establishes a concrete case in which geometric distortion substantially changes solving under identical controls. It does not establish the best geometric-arm pulse, a result averaged over instances, or medium-scale behavior. The pulse and formulation were selected using development data. [Paired independent reference](tail_validation/paired_results.json).

## New-layout classical endpoint check

For the actual serialized 20-atom operational inputs, exhaustive enumeration confirms that all three intended models have only correct minima, whereas all three geometric models have a unique assignment-invalid minimum. This includes the retuned formulation whose mean interaction error improved in the cross-instance placement comparison. Lower matrix error therefore did not restore a feasible endpoint minimum on this development instance.

The six intended target-correct configurations split into two exact rounded minima. Their energy spread from serialized field rounding is about \(1.1\times10^{-5}\) to \(1.9\times10^{-5}\) radians per microsecond. All six remain desired answers for our original-problem metric; “target-ground success” must not be confused with measuring occupancy of only the two actual rounded minima.

Bounded classical solves of the three actual 45-atom geometric endpoints also find infeasible minima. Separate feasible-set minima exclude every feasible tie, with energy separations above 42 radians per microsecond. Intended 45-atom generic proofs hit the preset ten-second limit. Separate deterministic perturbation checks combine certified invalid-encoding gaps with the enumerated feasible nonoptimal cost gap and the actual field-rounding span. All three retain strictly positive separation from every incorrect or nonoptimal state. Thus all six intended endpoints are certified correct, while none of the six geometric endpoints has a feasible minimum. Eleven bounded solves remain recorded as timeouts; their incumbents are not promoted to optima. [Completed independent endpoint report](medium_endpoint_audit/REPORT.md).

These conclusions concern one medium instance and the current selected layouts, not all possible placements. All quantum runs remain in the study: successful finite pulses can populate feasible excited states even when the endpoint ground state is wrong. [Endpoint evidence](medium_endpoint_audit/results.json).

## What remains before completion

The [completion checklist](COMPLETION_CHECKLIST.md) preserves the full scope. The small-problem tuning and per-instance matched-pulse results are complete. Required remaining medium-scale work includes both-objective selection, finalized per-instance matched-pulse evaluations, numerical refinement, tensor-approximation convergence, quantum evaluation of the retuned penalties, and an honest best-found-under-budget comparison. Rare-event claims must remain within the available numerical accuracy. Extremely small computed probabilities are not certified merely because total variation is below a much larger threshold.

A low per-shot probability does not automatically mean failure to find a solution in a batch. For independent shots from a fixed accurate distribution,

\[
P(\text{at least one success in }S\text{ shots})=1-(1-p)^S.
\]

Final reports must show per-instance probabilities and numerical limits before using this expression. Mean rates can hide a difficult case. No quantum speedup or advantage is established by this study.

## Official references

[Pasqal interaction overrides](https://docs.pasqal.com/pulser/apidoc/_autosummary/pulser.backend.EmulationConfig/) replace distance-derived pair coefficients. [Pulser's QUBO tutorial](https://pulser.readthedocs.io/en/v1.6.2/tutorials/qubo.html) distinguishes encoding from ground-state preparation. [DMM documentation](https://docs.pasqal.com/pulser/v1.3.0/apidoc/_autosummary/pulser.channels.DMM/) distinguishes per-site and aggregate detuning bounds; it does not establish the cause of our remote failures. [MPS numerical error documentation](https://pasqal-io.github.io/emulators/latest/emu_mps/advanced/errors/) explains why tensor approximation requires separate convergence checks.

## Reporting correction

The medium reduced selected rule doubles the LP assignment penalty; it does not weaken it. Earlier progress messages and the operational addendum used “weaker” as a shared label for both new formulations. That description was incorrect for reduced encoding. The selected slack rule does weaken its penalties. All selected numerical parameters, geometry errors, and experimental budgets are unchanged. Frozen inputs retain their historical identifiers with a correction sidecar, preserving reproducibility.

## Full medium budget and early pilot interpretation

After the user confirmed unlimited emulator access, the full development budget was frozen at 600 logical runs before inspecting any operational-pilot performance: 25 shared pulse candidates, two development cases, three formulations, two encodings and both interaction arms. The 36 pilot runs are included only where inputs match exactly. Separate search-seed winners and original-problem versus complete-encoding objectives are retained. Subsequent case evaluation and numerical refinement remain mandatory. [Frozen budget and selection protocol](medium_search/full_development_budget.json). This confirms access coverage, not an independently verified dollar price.

The first four pilot runs illustrate why matched pulses and separately tuned arms are both necessary. For the alternative reduced formulation on one case, baseline feasible counts were 8,366 intended versus 265 geometric; the short candidate instead gave 1,725 intended versus 3,546 geometric. Optimal counts for that short candidate were zero intended versus nine geometric. All rows contain 20,000 samples. These are incomplete development results, not selected winners or generalization evidence. The declared full budget is unchanged. [Current pilot scores](medium_operational_score.json).

## Full medium input and reuse verification

Independent review passed all 600 input digests, 300 matched pairs, 12 exact coefficient reconstructions and 36 byte-identical reused runs. The 100 original reduced development rows remain diagnostic-only because that formulation fails correctness on one evaluation case. This verifies construction, not quantum convergence or tuning success. [Independent review](full_medium_review/REPORT.md).

The scorer now rejects altered reuse declarations, source-manifest hashes and source-input digests. Eleven focused regression tests pass, including failed or missing source results, changed inputs and attempted double counting. Reused results contribute logical study coverage but no new observations or samples. The missing original-reduced evaluation layout was independently constructed with the same two-start fitting budget and remains selection-ineligible.

## Evaluation and accuracy-check readiness

The reviewed development batch is queued behind the pilot and eight baseline refinements, with four concurrent cloud jobs maximum. The frozen-protocol selector is implemented and passes nine focused tests. It refuses incomplete development data, excludes known-incorrect formulations from selection, retains shared-baseline dependence, and prepares 24 winners with 144 paired evaluation and 36 diagnostic baseline plans. No actual winners have been selected.

A numerical-observable checker now implements the predeclared absolute/relative tolerance and conservative differences of marginal Wilson intervals. Ten focused tests pass. It distinguishes pass, material failure and unresolved sampling uncertainty; zero counts retain positive upper bounds. This checks four observables only and does not independently verify model identity or prove exact dynamics. Integration with completed refinement runs and independent review remain pending.

## Finer local medium reference timeout

The geometric 20-atom 5-nanosecond local reference reached its predeclared 1,200-second wall-clock cap after 703 of 800 steps. No final state or probabilities were produced. The intended-arm finer reference remains available, but geometric timestep stability and the predeclared fine-reference whole-distribution comparison remain incomplete. The timeout is retained; a deferred rerun resource plan will be frozen separately before execution, without changing its scientific inputs.

At 6:36 am ET the independent tuning audit verified 416/512 fresh assignment-objective trials and 216/432 fresh complete-encoding trials. It verified 110 immutable hashes and all available metric, selection and fine-convergence checks. Cached warmstarts remain separate from fresh trials: 108 reused records correspond to 36 distinct frozen observations. These are progress counts, not final performance conclusions.

The baseline numerical comparison now verifies same-model/pulse provenance and exact permitted numerical-setting changes before applying its four-observable gates sequentially. All eight comparisons currently report incomplete because the refinements have not finished; none is promoted to a pass.

## Independent numerical-check review and reference retry authorization

Independent review passed the numerical checker and sequential baseline wrapper. A tolerance-boundary mismatch was corrected to match the frozen strict criterion: an exact difference at the tolerance fails; a sampled interval touching the boundary is indeterminate. Eleven regression tests and seven independent boundary cases pass. The eight pending refinement comparisons remain incomplete, not successful. [Independent numerical review](nonlinear_independent_review/numerical_gate_review_strict.json).

One fresh geometric 20-atom finer-reference attempt is authorized with unchanged scientific inputs and a 3,600-second monotonic wall-clock cap, deferred until the assignment-focused search exits. No checkpoint was available from the timed-out attempt. This resource-only change is frozen before the rerun, retains the original failure, and permits no selective resampling. [Deferred retry plan](local20_reference/deferred_retry3600_plan.json).

## Logical evaluation scoring review

The evaluation scorer independently passed six regression tests and four additional provenance/deduplication checks. Four logical selections pointing to two actual observations retain exactly 40,000 total samples. Identical count values in four genuinely separate result folders retain four observations and 80,000 samples. References through development aliases resolve to the underlying observation, and altered source locations or dependency manifests are rejected. This verifies sample accounting, not selection validity or numerical convergence. [Independent review](full_medium_review/logical_score_review/REVIEW.md).

## Independent evaluation preparation review

Evaluation preparation passed 14 existing tests and 381 independent temporary-input checks, including all 276 logical evaluation/development-refinement cases. In the synthetic selection fixture, 180 evaluation cases map to 48 physical runs; this is a deduplication test, not a prediction of the actual winner count. Both refinement branches preserve exact serialized controls and alter only declared numerical settings. The known-incorrect diagnostic case remains excluded from winner selection, and incomplete real development results block preparation before writes. No actual winners or evaluations were created. Actual future batches still require their own input review. [Independent evaluation review](full_medium_review/EVALUATION_REVIEW.md).

## Reporting limitation found in small-search outputs

Independent inspection found that the complete-encoding search saves derived 2,000-shot success estimates even for extremely small probabilities, although its whole-distribution convergence threshold does not establish their relative accuracy. Those derived fields will not be promoted into final conclusions without independent validation for the exact case, pulse and interaction model. The existing one-case rare-tail reference cannot certify other tuned winners. Frozen raw outputs remain unchanged.

The assignment-focused search has three TPE search seeds and one random-search seed, each with 32 fresh trials. The complete-encoding search has three TPE seeds with 24 fresh trials plus 12 shared cached warmstarts per study and no random-search comparator. Differences between these two stages also involve pulse families and formulation/layout menus, so they cannot be attributed solely to changing the optimization objective. A separate aggregation layer will preserve these distinctions and refuse a final report when cases or numerical gates are incomplete.

## Small-study aggregation independently verified

The separate reporting layer passed 12 focused tests and independent malformed-data probes after correcting input-file hash checks, probability consistency checks, development-case identities and fresh-trial accounting. These were validation defects in the newly written reporter, reproduced with synthetic inputs; actual saved records showed no unexpected integrity failures. Frozen experiments were not changed. Final aggregation refuses incomplete budgets, missing case/arm outputs or failed numerical checks. It preserves all search seeds and excludes unsupported repeated-shot predictions. [Independent review](full_medium_review/SMALL_AGGREGATE_REVIEW.md).

## Cloud observer suspension and recovery

At 7:07 am ET, operating-system inspection found the cloud observer and two waiting schedulers suspended despite their process IDs still existing. Earlier existence-only checks missed this. Server inspection confirmed that existing jobs were still running or complete. One resume recovered a result but the processes were suspended again. The precise external suspension cause remains unidentified; no terminal was attached.

The old observer drained its single in-flight submission, journaled its handle, and exited through its existing graceful-stop handler. Both old waiting schedulers also exited. A detached sequential controller then resumed the same frozen batches, same four-job concurrency cap and saved handles. No ambiguous submission remained and no experiment was restarted to replace a missing observation. The controller and observer remained active beyond the earlier resuspension interval, and the pilot reached 16 completed jobs at 7:13 am ET. This was execution recovery; scientific inputs and study scope were unchanged.

The replacement cloud controller passed 674 independent checks covering frozen inputs, process ownership, submission journal identity and sequential execution with a four-job limit. No duplicate handles were found. At 7:14 am ET, 17 pilot jobs were complete and four were active; later batches had not started. Failure within a stage does not cancel other already-authorized jobs in that stage, but prevents progression to later stages unless every required source succeeds. [Independent controller review](full_medium_review/pipeline_review.json).

## Completed assignment-focused tuning: scientific interim

All 512 trials and 320 case/arm evaluations are complete with saved refinement checks passed. For the alternative formulation, the three searches trained on exact interactions give 84.1–95.6% mean feasibility across five saved evaluation instances, dropping to 27.2–35.6% under geometric interactions with the same controls. Correct original-assignment probabilities are 41.5–49.4%, but complete-encoding probabilities are only 0.221–7.63% on exact interactions. Their geometric complete-encoding estimates are below the 0.1% reporting floor, which is not a certified upper bound. The equal-budget random run is competitive and exceeds those adaptive runs in mean original-optimum probability. One random seed and retrospective cases preclude general optimizer-superiority claims. [Full per-seed and per-instance interim](small_results/ASSIGNMENT_INTERIM.md). The separate complete-encoding objective remains unfinished.

The first medium development case also illustrates that lower matrix error is not enough. Doubling the alternative assignment penalty reduced coupling error from 0.7281 to 0.5934, yet geometric feasibility under the baseline pulse settings decreased from 265/20,000 to 1/20,000 samples. The two other predeclared pulse settings also had lower geometric feasibility after this change. Formulation, fitted geometry, scale and final detunings change together; this is a concrete proxy-metric limitation, not a controlled attribution to penalty size or a final tuned comparison. [Frozen-source pilot evidence](medium_search/reduced_retuning_pilot_interim.json).

## Finer medium reference completed

The unchanged geometric 20-atom reference retry completed at 7:25 am ET after 596.2 seconds of simulation. Halving the timestep changed feasibility by about 0.000001095 absolute, leaving it at 3.8912%; whole-distribution total variation was about 0.00002479. This completes the previously missing geometric refinement comparison while retaining the original timed-out attempt. It is empirical stability under one timestep change, not a rigorous universal error certificate.

The predeclared cloud-versus-fine-local distribution diagnostics returned Monte Carlo tail probabilities of 0.7166 for intended interactions and 0.08046 for geometric interactions; neither crossed the declared two-test threshold of 0.005. Each used 20,000 cloud samples and 2,000 calibration replicates. Low-expected-count states were pooled, so these results do not resolve the previously documented rare-category discrepancies. No new cloud samples were selected to erase those observations. [Distribution checks](local20_reference/global_cloud_check.json), [timestep comparison](local20_reference/geometric_comparison.json).
