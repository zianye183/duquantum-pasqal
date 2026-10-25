# Submission review

## Corrections made

- The previous exported CSV used the initial operational ledger. It omitted two successful retry results. The submission now uses the final scientific ledger: 209 completed primary conditions and 31 preparation failures.
- The best observed large-instance CVRP gap is **16.19%**, replacing 24.46%. The feasibility and optimum-rate table already used final results and is unchanged.
- Removed dependence on local absolute paths from the submission entry point. Original provenance paths remain as historical data.
- Kept all original denominators and distinguished problem counts, layout counts, raw shots and computed state probabilities.
- Preserved the original research narrative separately. Historical “alternative” penalty labels are explained as known-answer-informed diagnostics, not alternative assignment encodings.

## Executed checks

- 2,545 pinned evidence files checked.
- 20 seeded instances regenerated and feasibility certificates validated.
- 303 condition references independently rescored from raw counts; all 209 completed primary rows checked against the corrected CSV.
- Completed pulse aggregation reconstructed: 512 + 432 fresh trials, 16 + 18 winners, 320 + 360 case/arm evaluations.
- All 12 historical fixed-pulse cloud conditions rescored locally.
- All 18 small matched distributions independently rescored, then rerun from fresh layout fitting and dynamics. Maximum feasible/optimal probability difference: **0.0** on the tested environment.
- 20 CPLEX solves reproduce ten small clustering and routing references.
- 534 exhaustive classical case/variant checks pass; six additional medium checks agree with stored optimization results to numerical precision.
- All four saved medium reference distributions, timestep differences and grouped cloud diagnostics independently rechecked.
- All six reported mean embedding errors recomputed.
- All 12 pulse-aggregation regression tests pass.
- Final report rendered and verified at four pages. Main guide local links resolve.
- No credential-pattern matches or files over 90 MiB in the publication set. This is a targeted scan, not a formal security certification.

The full replay with fresh small simulations and CPLEX took **95.492 seconds**. No cloud jobs were submitted and no new cloud charges were incurred.

## Limits retained

Larger MPS numerical convergence remains unresolved. Full one-hot medium/large matched comparisons are untested. Historical tuning is retrospective and some diagnostic penalties use known answers. Quick replay validates saved evidence; it does not rerun every historical cloud job or prove every reference from scratch. The checked-in source inventory documents wider exploratory studies, whose results are not pooled with primary experiments. The team must review the final challenge submission.

Review recorded: 2026-10-25T11:14:32.585733-04:00
