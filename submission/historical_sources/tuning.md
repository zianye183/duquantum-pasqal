# Bounded ideal-encoding tuning pilot

**The tuned setting improved final-test feasibility, but this pilot shows no advantage for Optuna's adaptive search over random search. Neither method was tested on a quantum simulator.**

Protocol, instances, search ranges, objective, and tie policy were saved before tuning. The pilot used 24 fresh six-customer, three-vehicle instances: eight training, eight validation, and eight final-test instances. All 4,096 reduced-encoding states were evaluated exactly. Every mathematical ground-state tie was given equal weight; all reported configurations had six tied vehicle relabelings per instance. This weighting is not a physical output distribution.

Optuna 4.9.0 ran 40 TPE settings and 40 random settings with matching search budgets. Selection used training utility only. The two selected configurations were saved before either held-out cohort was evaluated. Both searches selected their identical first random candidate; subsequent trials did not beat it. There is one search seed, so no sampler-superiority claim is supported.

## Results

| Cohort | Fixed-rule feasible | Tuned feasible | Fixed-rule original optimum | Tuned original optimum |
|---|---:|---:|---:|---:|
| Training | 6/8 | 8/8 | 5/8 | 5/8 |
| Validation | 7/8 | 7/8 | 2/8 | 1/8 |
| Final test | 6/8 | 8/8 | 2/8 | 3/8 |

The validation loss of original optima matters: the tuned setting does not uniformly improve solution quality. The final test is small and supports further experiments, not a scaling or physical-performance claim.

The selected balance multiplier is 5.555755073. The assignment-penalty multiplier is 0.2490937325, applied to the bound recalculated at the new balance weight. The latter weakens the sufficient bound and loses its general invalid-code guarantee. It happened to preserve valid ground states on these observed instances.

The frozen objective gives invalid or infeasible ground states zero utility. A feasible state receives 0.75 plus 0.25 divided by one plus its relative original-clustering gap. Utility is averaged over every tied ground state and then over training instances. Raw penalized energy is never the cross-setting objective. Undefined feasible quality is retained as null when no ground state is feasible.

## Cost, verification, and scope

Science runtime: 2.454 seconds. Completed: 80/80 trials; 640 training-instance evaluations, 48 held-out evaluations, and 24 baseline/training-assessment evaluations. Cloud submissions: zero. Quantum measurements: zero. The local process had a 600-second science limit and used one worker. Total setup/install time is not included in the science runtime.

Independent verification matched all 72 baseline/selected configuration-instance ground-state sets to the full saved-form polynomial. Maximum energy difference was below 2.68e-12. The 24 instance seeds are distinct from one another and from the existing scaling benchmark. Trials and study storage remain available.

This is reduced-encoding mathematics only. It does not test embedding, atom placement, coupling fidelity, pulse parameters, finite-time quantum dynamics, medium/large scaling, or hardware. A physical tuning phase needs a new frozen design and an explicit compute budget.

## Reproducibility

Install command: `.venv/bin/python -m pip install --target audit/scaling/tuning_pilot/deps 'optuna==4.9.0'`. The dependency target is explicitly excluded by this folder's `.gitignore`; project environment and lockfiles were not changed. Exact installed versions are recorded in `freeze.json`, and the install transcript is retained.

Artifacts: `protocol.json`, `instances.json`, `freeze.json`, `studies.sqlite3`, `trials.jsonl`, `selected_before_holdout.json`, `results.json`, `verification.json`, and `pilot_summary.png`/`.pdf`. Reproduce in a fresh output directory; the runner refuses implicit overwrite/repetition of an existing study.

The pinned [Optuna TPE documentation](https://optuna.readthedocs.io/en/v4.9.0/reference/samplers/generated/optuna.samplers.TPESampler.html) describes the sampler; the [pinned package release](https://pypi.org/project/optuna/4.9.0/) identifies the dependency used.
