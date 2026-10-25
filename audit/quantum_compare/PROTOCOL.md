# Exact-target versus geometric quantum comparison

## Objective
Determine whether pair-interaction encoding errors cause loss of feasible and optimal solutions, separating formulation correctness, dynamics, and numerical error. Focus on 14-bit small slack, 20-bit medium reduced, and 45-bit medium slack. Tune pulses and compare original and certified alternative formulations. Alternatives using known optimal answers are diagnostic, not transferable policies.

## Gates and milestones
1. Independent code review, matrix/sign/order checks, full-state numerical convergence, and classical certificate validation.
2. Freeze source hashes, target/layout selection, identical-pulse paired cloud baseline inputs before outcomes. Twelve pilot jobs: first instance in each of three families, two formulations, two interaction arms.
3. Small pulse search: three independently seeded Optuna studies, 32 trials each per formulation/interaction arm, plus an equal single-study 32-trial random comparator. Optimize mean original-optimal probability on first three ascending-seed cases. Next two validate finalist choice; last five retrospective evaluation. All cases already observed in previous studies: no untouched-test claim. Keep study-seed variation visible.
4. Evaluate each selected pulse on both interaction arms. Distinguish same-pulse causal comparisons from equal-budget independently tuned performance. Refine local time integration for finalists, and independently check representative finalists on cloud.
5. Medium cloud pilot determines measured runtime and feasibility of pulse shortlist search. Freeze the medium candidate set, equal-arm budget, development/validation/evaluation allocation before new tuning outcomes. Evaluate both 20-bit and 45-bit families; do not substitute small evidence for medium. Certify MPS approximation with stronger numerical settings on representative cases.
6. Final report: feasibility, optimality, helper consistency, raw denominator, all cases, problem-level uncertainty, failures/rejections, actual cloud submissions and unknown charges. Separate feasible assignment from exact full-QUBO ground configuration.

## Controls
Matched pairs share initial all-zero occupations, pulse, duration, linear fields, target-to-physical energy conversion, backend, shots, noise and numeric settings. Only pair interactions change. Static interactions stay active throughout evolution. Intended linear endpoint is minus the detuning; final transverse drive vanishes. Physical geometric interactions reconstructed from serialized coordinates. Arbitrary matrix overrides and exact per-site fields are emulator diagnostics, not claims of hardware implementability.

## Acceptance
No conclusion from matrix-relative error alone. Report direct sampled or converged full-state probabilities. Correct QUBO ground states do not guarantee quantum preparation success. No feasibility guarantee for unverified baseline penalty rules. MPS conclusions remain provisional if bond/timestep convergence is unresolved. Record failures, timeouts, and missing cases without dropping them. Existing placement experiments in another worktree are outside this run and must not be stopped or modified.

## Execution ownership
Cloud worker owns preparation, frozen common geometry selection, baseline submissions and cloud evidence. Dynamics worker owns small local tuning and numerical convergence. Independent reviewer checks conventions and official documentation. Parent owns protocol, medium tuning scope, synthesis, durable status. New local tuning uses at most one computational worker while older placement jobs share this host.
