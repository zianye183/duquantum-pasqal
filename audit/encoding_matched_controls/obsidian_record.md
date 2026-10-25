---
categories:
  - "[[Research Projects]]"
tags:
  - llm_generated
created: 2026-10-25
codex_chat_id: 01a17323-204d-7b00-98cd-f0ded577afe9
codex_chat_title:
type: experiment
project: "[[Project - DuQuantum Pasqal]]"
status: completed
---
# Abstract
> [!abstract] Compare exact and geometric pair interactions across capacity slack, full one-hot balance, and reduced balance on three shared small problems.

# LLM Prompt
Don't use "alternative weights". It is pretty confusing. Do we have the same experiments but for our alternative encoding methods? If not, do it now

# Hypothesis and decision
Pair distortion can reduce success, but encoding correctness and finite pulse duration can also limit success. Distinguish these when presenting the challenge results.

# Design
Three fixed existing small cases, three encodings, one BLaDE layout each. Penalties require no optimal answers. Same pulse/fields/scale within every exact/geometric pair. Local full-state integration, step-halving checks and independent adaptive integration. No cloud submissions. Inspect per-case results rather than only averages.

# Evidence
/Users/alanye/.codex/worktrees/2da4/duquantum-pasqal/audit/encoding_matched_controls/PROTOCOL.md

# Human judgment
My first read: pending. Most suspicious artifact: any feasible-rate gain under distorted interactions. Decision affected: whether embedding is a bottleneck across encodings.

# Results and closeout
- Completed at 10:46 am ET on October 25, 2026. Measured run time 75.3 seconds. Zero cloud submissions or new cloud charges.
- Three shared small problems, nine BLaDE layouts, 18 distributions. Mean feasible exact/geometric probabilities: slack 7.8128%/1.0985%; full one-hot balance 21.6069%/10.5518%; reduced balance 36.0506%/24.0008%.
- Observation: feasibility and original optimality decrease in all nine pairs. Both balance models already have an infeasible intended minimum on one case. Geometry restores its reduced ground-state correctness but still worsens finite-pulse success.
- Validation: all-state polynomial checks for nine models, 18 timestep checks, 18 separately rescored distributions. Two eight-bit arms agree with independent DOP853 integration.
- Interpretation: pair distortion matters across all three tested encodings; it is not the only bottleneck. Small retrospective population, one layout per case, fixed analytic pulse and ideal individual fields. Full one-hot medium remains untested.
- Evidence: [Experiment report](/Users/alanye/.codex/worktrees/2da4/duquantum-pasqal/audit/encoding_matched_controls/REPORT.md), raw results and distributions in the same directory.
- Presentation replaces ambiguous penalty-variant rows with these encoding comparisons. Historical medium cloud evidence remains separately labelled.
- Human review: inspect the case where geometry restores the correct minimum but reduces sampling success. No additional run is active.
