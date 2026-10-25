# Completed assignment-objective tuning: interim evaluation

The alternative formulation produces substantially higher assignment success in this diagnostic, but geometric interactions still reduce performance and leave severe instance-to-instance variation. Across the three searches trained on intended interactions, evaluation feasibility averages 84.1–95.6% for the alternative formulation versus 9.0–9.85% for the original formulation. Applying each identical alternative-formulation pulse to geometric interactions lowers mean feasibility to 27.2–35.6%; the worst instance is below 0.1% for every seed. This is formulation-dependent evidence, not a guarantee of generalization or deployable penalty selection.

Adaptive optimization did not consistently beat the equally budgeted random search. For the alternative formulation, the single random-search run has higher evaluation mean assignment-optimum probability than each of the three adaptive runs on their respective training interaction models. This descriptive result does not prove random search generally superior; one random replication and 32 trials per run limit the conclusion.

This is the completed assignment-objective stage only. The other objective/pulse-family search is unfinished, and the global final-report gate remains unchanged. All 512 declared trials, 16 winners and 320 case/arm rows are present; all saved rows pass their empirical refinement checks. Evaluation uses five saved instances, with every winner tested unchanged on both interaction models. No evaluation outcome selected a winner or triggered a new simulation.

Each table entry is **mean [minimum] percentage across five instances**. **low** means the estimate is below the 0.1% reporting floor; it is not a certified upper bound and no relative precision is asserted. “Original optimum” accepts the correct clustering assignment even when its slack bits do not satisfy the full encoding; “full optimum” requires both. Training arm identifies the interaction model used for development optimization. All three adaptive-search seeds and the one equally budgeted random run are retained separately.

## Original formulation; trained on intended interactions

| Search | Evaluated interactions | Feasible | Original optimum | Full optimum |
|---|---|---:|---:|---:|
| tpe 11 | intended | 8.99 [6.1] | 3.94 [3.08] | 0.427 [0.157] |
| tpe 11 | geometric | 3.34 [0.585] | 0.606 [low] | low [low] |
| tpe 29 | intended | 9.02 [0.906] | 4.08 [0.338] | 0.858 [low] |
| tpe 29 | geometric | 2.87 [low] | 0.164 [low] | low [low] |
| tpe 47 | intended | 9.85 [1.17] | 4.45 [0.442] | 0.969 [low] |
| tpe 47 | geometric | 2.17 [low] | 0.361 [low] | low [low] |
| random 11 | intended | 8.99 [6.1] | 3.94 [3.08] | 0.427 [0.157] |
| random 11 | geometric | 3.34 [0.585] | 0.606 [low] | low [low] |

## Original formulation; trained on geometric interactions

| Search | Evaluated interactions | Feasible | Original optimum | Full optimum |
|---|---|---:|---:|---:|
| tpe 11 | intended | 1 [0.115] | 0.387 [low] | low [low] |
| tpe 11 | geometric | 1.58 [0.806] | 0.4 [0.116] | low [low] |
| tpe 29 | intended | 3.91 [2.13] | 1.62 [0.975] | 0.118 [low] |
| tpe 29 | geometric | 1.69 [0.568] | 0.75 [0.18] | low [low] |
| tpe 47 | intended | 8.99 [6.1] | 3.94 [3.08] | 0.427 [0.157] |
| tpe 47 | geometric | 3.34 [0.585] | 0.606 [low] | low [low] |
| random 11 | intended | 8.99 [6.1] | 3.94 [3.08] | 0.427 [0.157] |
| random 11 | geometric | 3.34 [0.585] | 0.606 [low] | low [low] |

## Alternative formulation; trained on intended interactions

| Search | Evaluated interactions | Feasible | Original optimum | Full optimum |
|---|---|---:|---:|---:|
| tpe 11 | intended | 95.6 [84.7] | 49.4 [44.1] | 7.63 [1.92] |
| tpe 11 | geometric | 35.6 [low] | 28.6 [low] | low [low] |
| tpe 29 | intended | 84.1 [65.6] | 41.5 [33] | 1.1 [low] |
| tpe 29 | geometric | 30.4 [low] | 23.8 [low] | low [low] |
| tpe 47 | intended | 94 [84.5] | 47.7 [40.1] | 0.221 [low] |
| tpe 47 | geometric | 27.2 [low] | 25.2 [low] | low [low] |
| random 11 | intended | 96.8 [89.5] | 50 [43.1] | 2.18 [low] |
| random 11 | geometric | 39.2 [low] | 34.5 [low] | low [low] |

## Alternative formulation; trained on geometric interactions

| Search | Evaluated interactions | Feasible | Original optimum | Full optimum |
|---|---|---:|---:|---:|
| tpe 11 | intended | 97.7 [91.8] | 51.3 [44.9] | 2.32 [low] |
| tpe 11 | geometric | 35.6 [low] | 32.6 [low] | low [low] |
| tpe 29 | intended | 98.8 [95] | 53.8 [50] | 11.9 [4.07] |
| tpe 29 | geometric | 39.3 [low] | 33.7 [low] | low [low] |
| tpe 47 | intended | 91.1 [78.1] | 45.3 [38.5] | 0.498 [low] |
| tpe 47 | geometric | 35.6 [low] | 30.3 [low] | low [low] |
| random 11 | intended | 96.8 [89.5] | 50 [43.1] | 2.18 [low] |
| random 11 | geometric | 39.2 [low] | 34.5 [low] | low [low] |

## Per-instance paired evidence

The JSON contains all 80 winner/instance pairs, both sets of probabilities, their geometric-minus-intended differences, identical pulse parameters, numerical histories summarized by final step and adjacent-step discrepancy, source paths and hashes. It also contains all 24 separate equal-budget adaptive-minus-random comparisons. The same random result is reused, so these comparisons are not independent replications.

## Interpretation limits

- Evaluation instances were already inspected in earlier work; retrospective rather than untouched test set.
- Both formulations valid, but alternative formulation oracle-informed; not deployable penalty learning.
- Development-only selection preserved; evaluation outcomes do not choose winners or trigger retuning.
- Three TPE seeds retained individually; one random seed per formulation/trained arm reused across comparisons; no pooled-best TPE claim.
- Empirical successive-step TV<0.001 supports only absolute stability; rare full-encoding probabilities below0.001 have no relative-precision guarantee.
- No many-shot success predictions exported. No hardware validation or noise model.
- Other objective/pulse-family study remains unfinished, so this is not the final goal report.
