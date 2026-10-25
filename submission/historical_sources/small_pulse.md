# Completed small-slack quantum tuning study

**Both searches completed: 944 fresh trials, 34 retained winners and 680 instance/arm evaluations. All reporting gates passed.** This report concerns fourteen-atom slack encoding; it does not complete the separate medium-scale study. The paired comparisons show that geometric interactions can materially damage solving, while exact interactions alone do not guarantee success.

When optimizing complete-encoding success, intended-trained alternative-formulation runs achieve **11.8–23.7% mean complete-optimum probability** on the five evaluation instances with exact interactions. The corresponding original formulation reaches **1.33–2.26%**. For those identical pulses under geometric interactions, all complete-optimum means fall below the reporting floor. Even training directly on geometric interactions leaves the highest mean complete-optimum probability at approximately **0.168%**, with much poorer individual cases. These are findings within the tested controls and retrospective instances, not a proof that better optimization is impossible.

Assignment-only optimization answers a different question. Intended-trained alternative runs reach **84.1–95.6% mean feasible assignments** and **41.5–49.4% mean optimal assignments**, while complete-encoding optimum probability ranges from **0.221–7.63%**. A correct assignment can therefore coexist with wrong slack bits. Switching to the complete-encoding objective also changed the pulse family and formulation/layout menu; its different results cannot be attributed solely to the objective.

## Design and completion

| Stage | Fresh trials | Optimizer runs | Retained winners | Case/arm rows | Comparator |
|---|---:|---:|---:|---:|---|
| Assignment optimum | 512 | 16 × 32 trials | 16 | 320 | Three adaptive seeds and one random seed per formulation/training arm |
| Complete-encoding optimum | 432 | 18 × 24 fresh trials | 18 | 360 | Three adaptive seeds; no random comparator |

Each winner was selected using only three development instances, then evaluated unchanged on two validation and five evaluation instances in both interaction models. All three optimizer seeds are retained. The second stage also used twelve shared cached warm-start points per formulation/training arm; reusing them across optimizer seeds does not create independent trials or observations. Its physical layout fits used the separate fixed-budget formulation study. Alternative formulations use the known optimum during construction, and all saved instances had been inspected previously.

## Evaluation across optimizer seeds

Entries show the **range of the three adaptive-search means [lowest individual-case probability across those runs]**, in percent. This range is descriptive, not a confidence interval. “low” means an estimate below the **0.1% reporting floor**, with no relative-accuracy claim or certified upper bound. Training identifies the interaction model used during development optimization; evaluation identifies the model used to propagate that identical selected pulse.

### Assignment-optimum objective

| Formulation | Trained on | Evaluated on | Feasible | Original optimum | Complete optimum |
|---|---|---|---:|---:|---:|
| Original | intended | intended | 8.99–9.85 [0.906] | 3.94–4.45 [0.338] | 0.427–0.969 [low] |
| Original | intended | geometric | 2.17–3.34 [low] | 0.164–0.606 [low] | low–low [low] |
| Original | geometric | intended | 1–8.99 [0.115] | 0.387–3.94 [low] | low–0.427 [low] |
| Original | geometric | geometric | 1.58–3.34 [0.568] | 0.4–0.75 [low] | low–low [low] |
| Alternative (oracle-informed) | intended | intended | 84.1–95.6 [65.6] | 41.5–49.4 [33] | 0.221–7.63 [low] |
| Alternative (oracle-informed) | intended | geometric | 27.2–35.6 [low] | 23.8–28.6 [low] | low–low [low] |
| Alternative (oracle-informed) | geometric | intended | 91.1–98.8 [78.1] | 45.3–53.8 [38.5] | 0.498–11.9 [low] |
| Alternative (oracle-informed) | geometric | geometric | 35.6–39.3 [low] | 30.3–33.7 [low] | low–low [low] |

### Complete-encoding-optimum objective

| Formulation | Trained on | Evaluated on | Feasible | Original optimum | Complete optimum |
|---|---|---|---:|---:|---:|
| Original | intended | intended | 10.5–14.2 [3.34] | 4.56–6.01 [1.2] | 1.33–2.26 [0.155] |
| Original | intended | geometric | 4.07–5.16 [low] | low–low [low] | low–low [low] |
| Original | geometric | intended | 1.14–1.89 [0.681] | 0.394–0.811 [0.335] | low–0.152 [low] |
| Original | geometric | geometric | 1.56–1.71 [low] | low–0.693 [low] | low–low [low] |
| Alternative (oracle-informed) | intended | intended | 93.7–96.9 [84.8] | 47.1–52.1 [40.6] | 11.8–23.7 [4] |
| Alternative (oracle-informed) | intended | geometric | low–low [low] | low–low [low] | low–low [low] |
| Alternative (oracle-informed) | geometric | intended | 12.5–33.3 [7.11] | 5.22–15.2 [3.49] | low–2.28 [low] |
| Alternative (oracle-informed) | geometric | geometric | 3.35–4.02 [low] | 1.28–2.54 [low] | low–0.168 [low] |
| Double assignment penalty (oracle-informed) | intended | intended | 91.1–95.7 [82.7] | 45–48.3 [38] | 11.2–13.2 [4.24] |
| Double assignment penalty (oracle-informed) | intended | geometric | 1.42–13.6 [low] | 1.41–13.4 [low] | low–low [low] |
| Double assignment penalty (oracle-informed) | geometric | intended | 19.1–63 [7.47] | 7.59–26.4 [2.76] | 0.246–0.539 [low] |
| Double assignment penalty (oracle-informed) | geometric | geometric | 15.4–19.5 [0.914] | 10.2–12.3 [0.238] | low–low [low] |

## Random search and uncertainty

Each adaptive assignment-objective run is compared separately with one random run having the same 32-trial budget. The random outcome is reused across comparisons; no best-of-three adaptive run is compared against a single random run. For the alternative formulation, the random run has higher evaluation mean assignment-optimum probability than every adaptive run on its respective training interaction model. This is descriptive evidence that the limited adaptive search did not consistently outperform random search here. It does not establish random search superiority: there is only one random seed per condition. The complete-encoding stage has no random comparator.

These are probabilities computed from simulated state vectors, so measurement-shot confidence intervals are inappropriate for these local results. Important uncertainty comes from five retrospective evaluation instances, three optimizer seeds, finite search budgets, numerical approximation, and idealized controls. Means can conceal severe worst-case failures. Optimizer seeds, repeated winners and matched interaction arms are not independent problem instances. No pooled confidence intervals or broad population guarantees are claimed.

## Numerical and physical limits

Every saved evaluation passed successive-step total-variation refinement below 0.001, and all final inputs, winners, splits, budgets and source hashes passed the separate reporting checks. This is empirical absolute stability, not a rigorous total dynamics error bound or relative precision for rare events. One separately validated tiny-tail example does not certify all winning pulses. Unsupported many-shot success predictions from source files are excluded.

Pulse controls here are ideal continuous analytic functions with individual fields. The complete-encoding stage uses the expanded beta-shaped detuning family, which was not serialized or validated for hardware by this study. Allowed durations extend beyond the real-device duration limit. Geometric coefficients come from the frozen placement artifacts; coordinate serialization errors are a separate limitation already documented in the geometry review. No device noise or hardware execution is established.

## Reproducible evidence

- `final.json`: all 340 winner/instance pairs across development, validation and evaluation, numerical checks, frozen source hashes and per-run fair-budget comparisons.
- `evaluation_details.csv`: all 68 evaluation study/arm summaries, each optimizer seed separate, including means, minima and rare-probability flags.
- `paired_evaluation.csv`: all 170 evaluation winner/instance pairs, both interaction models and their probability differences.
- `tests.log`: focused aggregation tests; independent review is retained separately in the audit.

The complete small-study result is useful evidence for the wider investigation. Medium-scale tuning, numerical refinement, and its separate evaluation remain separate requirements.
