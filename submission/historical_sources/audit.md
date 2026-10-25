# Notebook audit: concerns substantiated; no demonstrated fourteen-atom ceiling

## 1. What this is

Independent review of the DuQuantum–Pasqal challenge documentation and notebooks 1–4. **The reported limitations are partly real, but several conclusions are overstated or stale. The tested textbook algebra is correct; its poor sampling does not establish an atom-count ceiling.** Both physical mapping and untuned penalties matter. The reduced model also has a genuine capacity-modeling limitation.

This report supersedes conflicting claims in the reviewed handoff for this audit. Existing notebooks were preserved because other sessions were actively editing and executing them.

## 2. What was done

- Three independent reviewers audited the encoding, Pasqal integration, and experimental statistics.
- Exhaustively checked 1,064,976 binary states against independently evaluated mathematical objectives: 16,384 textbook states, 16 small reduced states, and 1,048,576 medium reduced states.
- Recomputed the 306-row multi-instance table, investigated excluded cases, and reviewed completed local and cloud outputs.
- Checked installed package implementations and official Pasqal/Pulser documentation. Installed versions were QUBO Solver 0.9.1, QoolQit 1.5.0, Pulser 1.9.1, and emu-sv 2.10.0.
- Examined 7,500 textbook penalty pairs, tested the reduced model mathematically on 100 fresh capacity-active instances, and ran six new Pasqal Cloud simulations.
- Read the separate research milestone and independent review. Its 100-instance physical study is a different implementation and population; its results are not pooled with these notebooks.
- Preserved source snapshots, submitted sequences, configuration, interaction matrices, cloud batch identifiers, and all new raw measurement counts.

## 3. Results

### The textbook encoding is correct on the checked problem

All exhaustive polynomial checks passed to numerical roundoff. Every exact minimum of the tested textbook and reduced baseline models decoded to the correct constrained clustering optimum. No sign or factor-of-two error was found in the QUBO Solver adapter. This establishes the checked algebra, not universal correctness of every possible instance or execution path.

The textbook model still represents only four customers with fourteen atoms. The six extra capacity bits and redundant truck-assignment bits consume much of the representation. Atom count alone does not measure physical difficulty.

### New cloud experiment: penalties materially change success

The original textbook weights were equal and conservative. An exhaustive diagnostic selected much smaller capacity weight while retaining the correct minimum. Its estimated usable final energy separation increased by 28.09 times. The existing notebook scan missed this region entirely.

All four cloud runs used the same small instance, the same pulse shape and amplitude, exact intended interactions, individual atom controls, and the same rule for using available interaction and detuning ranges. Each produced 10,000 measurements.

| Pulse duration | Penalties | Feasible answers | Optimal clustering answers | 95% interval for optimal rate |
|---|---|---:|---:|---:|
| Four microseconds | Original | 8.86% | 3.38% | 3.03–3.75% |
| Four microseconds | Adjusted | 16.94% | 10.58% | 9.98–11.20% |
| Six microseconds | Original | 12.22% | 4.77% | 4.36–5.21% |
| Six microseconds | Adjusted | 14.20% | 10.58% | 9.98–11.20% |

At four microseconds, adjusted penalties improved optimal sampling by approximately 3.13 times. Increasing duration did not improve the adjusted result. Therefore final energy separation alone is not a complete explanation; pulse dynamics still matter.

**Limits:** This is an answer-informed, single-instance diagnostic with artificial exact interactions, not a physical-device or held-out success claim. The energy scale is recomputed under the same maximum-range rule rather than inherited from the imperfect geometric fit, so these baseline numbers should not be substituted directly into the original notebook table. The confidence intervals describe measurement uncertainty for fixed simulations, not uncertainty across problems. Feasibility and optimality concern the decoded clustering; capacity-helper bits need not be exact. Exact full-model minimum probabilities remained only 0.30%, 0.48%, 0.66%, and 0.64%, respectively.

### Physical interactions also improve on this instance

The adjusted penalties were then refitted using the standard sixty-start placement routine. The fit took 41.43 seconds locally. Interaction error remained substantial, 39.14%, but the lowest-energy state now decoded to the correct clustering under both global and individual atom controls. This is a direct counterexample to treating the earlier bad layout as an intrinsic fourteen-atom barrier.

Two additional cloud simulations used the fitted distances, **without any interaction override**, at four microseconds and 10,000 measurements each:

| Controls | Feasible answers | Optimal clustering answers |
|---|---:|---:|
| Shared global control | 16.10% | 10.91% |
| Individual atom controls | 84.83% | 59.00% |

Independent raw-count and full final-energy checks passed for both. Exact 95% intervals for optimal clustering are 10.305–11.537% and 58.029–59.966%. The intended textbook ground-state counts are zero and 124 out of 10,000; most successful decoded clusterings therefore do not solve the full helper-bit QUBO exactly.

The earlier cloud smoke at the original penalties gave 0% optimal in both physical-interaction settings. The revised result changes both penalties and fitted geometry; it is not an isolated pulse comparison. It remains one answer-informed development instance. Global control passes the configured physical-device constraints; individual controls use an emulator-only device configuration. Neither is a hardware measurement. The best physical states have incorrect helper bits but correct feasible customer assignments, so **59% is a decoded clustering success rate, not exact textbook-QUBO ground-state probability**.

### The reduced model has a structural limitation

Replacing capacity slack with a common squared load penalty changes the problem into load balancing. Since total demand is fixed,

\[
\sum_k(L_k-Q)^2=\sum_k L_k^2-2Q\sum_i q_i+KQ^2.
\]

The capacity threshold contributes only a constant to assignment rankings. A balanced solution may respect capacity, but this is not an exact capacity constraint.

One of the original 26 problems was excluded because calibration failed. Independent exact inequalities show this is not a coarse-search issue: the desired answer would require both

\[
\mu>0.5363763110\quad\text{and}\quad\mu<0.4200114522.
\]

No such weight exists. The notebook crashes when all candidate weights fail; the shared helper avoids the crash but downstream studies omit the instance. Report this as one formulation failure out of 26, alongside metrics conditional on the remaining 25.

The new screening used 100 fresh feasible, capacity-active problems, disjoint from those 26. It found:

| Mathematical check, before any quantum simulation | Count |
|---|---:|
| Some balance weight can preserve the correct optimum | 96/100 |
| No balance weight can preserve it | 4/100 |
| Fixed equal-weight rule gives the correct optimum | 57/100 |
| Fixed equal-weight rule gives a feasible minimum | 61/100 |
| Fixed equal-weight rule gives an infeasible minimum | 39/100 |

This confirms a modeling limitation independently of physical placement, pulse choice, or measurement randomness. These instances are now inspected data, not an untouched test set for subsequent tuning.

### The multi-instance results do not support the headline

For the original 25 calibratable four-atom instances:

| Method | Median optimal-shot rate | Mean optimal-shot rate |
|---|---:|---:|
| Manual physical/global pipeline | 0.4% | 39.89% |
| Library physical/global pipeline | 2.3% | 28.35% |
| Exact-interaction diagnostic | 35.9% | 36.57% |

The manual result is strongly split between near-perfect and near-zero cases: 10 of 25 exceed 90% optimal. The 95% interval for the corresponding population fraction is wide, 21.1–61.3%. A 99% single-instance result is not representative. The ideal-interaction median is a fixed-schedule diagnostic, not a performance ceiling or practical solver benchmark.

The broader research study already reports a separate 100-instance physical result: a simple balanced random assignment achieves 32.33% mean optimal probability versus 19.38% for that physical implementation. Its population includes capacity-inactive cases and its implementation differs; this is corroborating context for stronger controls, not a direct replication of notebook 04.

## 4. Issues and gaps

### Confirmed errors and unsupported wording

| Item | Audit conclusion |
|---|---|
| Per-atom energy diagnostic in notebooks 03/04 | Actual code bug: detunings are taken in dictionary iteration order instead of register atom order. Corrected recomputation changes 7 of 51 saved library classifications. Correct optimal-minimum counts are 11/25 calibrated and 13/26 equal-weight, versus saved 7/25 and 12/26. Actual pulse execution and measured success rates are unaffected. Shared-control diagnostics are unaffected because every atom has the same detuning. |
| Textbook method is approximately zero feasible everywhere | False for updated per-atom control: 44.2% feasible locally and 44.0% in the reviewed cloud smoke; zero optimal samples. Global-control failure remains real. |
| Medium method is zero feasible under every setting | Too broad: saved exact-interaction diagnostic is 11.2% feasible, though no optimal samples. Physical settings remain poor. |
| Exact-interaction result is a 45.5% ceiling | Unsupported. One pulse and final energy spacing cannot prove a ceiling. |
| Embedding, not pulse, determines success | Overgeneralized. Wrong final minima explain failure of perfect slow ground-state following, but dynamics can populate other states; library pulse changes also alter success. |
| Pulse is generally robust | Sensitivity evidence is mainly one instance, not a held-out robustness study. |
| Reduced calibration always works | False, with an exact counterexample and four more among 100 new problems. |
| Notebook 02 comparison with textbook results | Stale copied values and descriptions of already-fixed pulse/scale problems. |
| Library runs labeled “plus postprocessing” | Both preprocessing and postprocessing are enabled. Preprocessing leaves the three present matrices unchanged, so this is a reporting/design flaw, not the cause of current numerical differences. |
| Cloud experiment provenance | Existing runner hashes imported helpers at completion and omits raw histograms and cloud identifiers from summaries. Concurrent edits can make the recorded hash describe different source. The new diagnostic snapshots inputs before submission. |

### Why fourteen atoms can still be difficult

The exact textbook model requests many different pair interactions, including zeros. Physical atoms supply distance-dependent positive interactions, with all distances constrained by one two-dimensional layout. One shared atom control also cannot reproduce arbitrary individual linear terms. Consequently a valid algebraic reduction can become the wrong physical energy function even at small atom count. Pasqal's [embedding documentation](https://pasqal-io.github.io/qubo-solver/latest/user_guide/quantum/embedding/) explicitly treats interaction error as a proxy rather than a guarantee of solution quality.

Large penalty coefficients additionally force the intended objective into a small fraction of the available energy range. The cloud comparison demonstrates that this choice matters, while its still-low success shows that correcting the scale does not solve the entire problem.

Pasqal's [Pulser QUBO tutorial](https://pulser.readthedocs.io/en/stable/tutorials/qubo.html) uses a deliberately favorable matrix and explains the importance of local controls for unequal diagonal terms and adapting pulse parameters to a different problem. It does not promise that a generic textbook QUBO maps faithfully or solves reliably simply because it has few variables. The library also exposes [alternative pulse-shaping methods](https://docs.pasqal.com/applicationsolvingtools/qubo/user_guide/quantum/drive_shaping/); comparing its default pulse against a developed manual pipeline is not a best-effort solver comparison.

### Remaining limits

- The 26-instance notebook study covers four atoms, not a multi-instance fourteen-atom scaling study.
- Calibration uses the known optimum. This classical information must be counted and cannot be presented as a deployable unknown-answer method.
- Measurement seeds, problem seeds, and atom-placement seeds answer different questions. More measurements cannot replace independent problems or independent placement attempts.
- Zero observed successes is not proof of zero probability. With 2,000 trials, its one-sided 95% upper bound is about 0.15% for that fixed setting.
- Comparisons need uniform vehicle assignments and a simple structured classical baseline, not only uniform raw encoding bits. Raw bitstrings disproportionately punish redundant encodings.
- No equal tuning-time budget or full held-out pulse/penalty study has been demonstrated. No noisy hardware result or numerical convergence check for every setting is claimed.
- At initial review the latest saved notebooks 03 and 04 contained no executed cells while other sessions reran them. By the 9:41 pm ET recheck, both had completed: eight of eight and seven of seven code cells executed, with zero saved errors. The library results table now contains 24 rows. This resolves the initial saved-execution gap, but successful execution does not detect the atom-order diagnostic bug. Completed text outputs were archived.

## 5. Current status

All six new cloud jobs completed successfully on October 24: the four ideal diagnostics between 9:37 pm ET and 9:38 pm ET, and the two physical-interaction followups between 9:40 pm ET and 9:41 pm ET. They produced 60,000 measurements. The two submission-to-final-retrieval intervals were approximately 57 and 39 seconds; these include queueing and retrieval and are not hardware runtimes. The inspected project and job interfaces do not expose charges, so exact money or credits spent is **unknown**, not zero.

The three independent reviews, 100-instance model screen, and local physical-placement check are complete. All six cloud runs passed independent recount and control checks. Physical-interaction results also passed independent full final-energy enumeration. All 51 small-instance library per-atom classifications were recomputed with explicit atom ordering. Nothing from this audit is running. Existing notebook source remains unchanged; the confirmed ordering defect and stale claims are documented rather than silently patched during other sessions' work.

## 6. Best next step

First fix the atom-order diagnostic, correct report language, and remove stale copied result tables. Then develop penalty and pulse rules on an explicit training set, freeze them, and evaluate a fresh multi-instance fourteen-atom physical benchmark with all failures retained and strong classical controls. Check that the realized energy preserves good answers before spending on extensive pulse scans.

Do not buy a large cloud sweep merely to repeat measurement randomness. The next useful spending is a bounded, predeclared comparison of independent instances and physical settings. Its cost and completion time are not yet measured; no credible estimate is available from this audit. No user decision is needed to accept the audit evidence. Further experiments should be scoped around the observed failure mechanisms.

### Evidence

- [Encoding review and exhaustive checks](encoding/report.md)
- [Statistical review](statistics/statistics_review.md)
- [Pasqal integration review and official references](pipeline/findings.txt)
- [New cloud configuration and job record](cloud_penalties/manifest.json)
- [New cloud results with intervals](cloud_penalties/summary.json)
- [Physical-interaction cloud results](cloud_penalties/physical_manifest.json)
- [Independent cloud validation](statistics/cloud_review.md)
- [Refitted physical placement](pipeline/tuned_geometry.json)
- [Corrected atom-order diagnostics](pipeline/library_dmm_order.json)
- [Held-out mathematical screening](encoding/heldout.json)
- [Reviewed-source inventory](reviewed_sources/manifest.json)
