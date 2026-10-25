# Frozen scope: selective weighted-wire redundancy pilot

## Question and interpretation

Does exact auxiliary-variable reformulation make the physical energy more faithful to the original QUBO, and does any improvement translate into better quantum sampling? This is an intervention on three fixed problems per family. It is not a claim that three problems represent the population or that selective wires exhaust redundancy schemes.

The literature-supported identity is

\[
\min_{a,b\in\{0,1\}}[-J(a+b)+2J(xa+ab+by)+J]=Jxy,\qquad J>0.
\]

Each removed logical edge receives two private ancillary atoms. With endpoints both zero there are two ancillary minima; other endpoint configurations have one. Thus static energy equivalence does not imply equal degeneracies, gaps or evolution. Full distance-derived interaction tails are retained. This selective use on dense QUBOs is a new diagnostic application of the published weighted-wire construction, not a reproduction of the paper's sparse-graph experiment.

## Instances, targets, levels

- Small slack: saved seeds 2002, 2006, 2012; 14 original bits.
- Medium reduced: saved seeds 2002, 2006, 2007; 20 original bits. Use the previously independently certified alternative target for ALL three. The original target on the third problem is suboptimal before embedding. This choice is based on mathematical correctness, not physical outcomes. These alternatives use reference-answer information and are diagnostic targets, not deployable held-out tuning.
- Medium slack: saved seeds 2002, 2006, 2007; 45 original bits, original conservative penalty model.
- Levels: zero, one, two replaced edges, adding zero, two, four atoms. Thus 14/16/18, 20/22/24 and 45/47/49 atoms.
- The same three problems are paired across every level. Repeated placements and controls are not independent instances.

This produces 27 target/layout cases and 54 main intended/geometric simulations. For all 15 cases above 20 atoms, both arms receive a numerical refinement: 30 additional simulations. Total initial scientific request: 84 runs, 4,000 samples each, 336,000 requested samples. A separate two-atom operational discriminator uses two 20,000-sample runs and is not scientific problem evidence.

## Geometry

Use eight fixed starts and at most 1,500 iterations per start at every level. Initializations combine target-distance spectral positions and spaced lattice positions with fixed jitter seeds. Preserve all attempted starts, convergence flags, physical checks and elapsed time. Select the physically legal layout with lowest enlarged pair-relative error; report the limitation that this score need not select the best logical energy landscape.

Fit the baseline first. Rank required positive original edges by absolute pair residual at its fitted scale. Replace the highest-ranked edge at the first redundancy level and the first two at the second level. Break ties lexicographically. This is nested and independent of the original optimum and quantum outcomes. Do not replace failed instances or add outcome-selected starts.

For each problem/formulation, set one common logical scale to the smallest individually device-allowed fitted scale among its three selected layouts. Expand the other coordinates uniformly to that scale. Retain minimum spacing and maximum radius checks using installed AnalogDevice values. A shared scale keeps logical energy bandwidth constant across redundancy levels. Geometries that become invalid remain recorded preparation failures, not silently relaxed devices.

Pre-submission amendment: one medium slack baseline exceeded the 38-micrometer radius after common scaling. Preserve all initial selections and the failure under `superseded/initial_common_scale`. At the already-fixed common scale, recheck all eight existing starts for every level of all nine groups and select the lowest-error legal candidate. This changes only that failed baseline. No extra fits, changed targets, changed common scales or quantum-result selection are allowed. Wire ranking remains frozen from the original discovery baseline. The complete decision is recorded in `common_scale_amendment.json`.

## Fidelity and static checks

Verify every augmented coefficient against an independent construction and the private-wire identity. For up to 20 original bits, enumerate logical states and minimize all auxiliary configurations. For larger targets combine the exact algebraic proof with fixed basis/random checks. Snapshot original coefficient files and certificates before use.

Measure physical logical energy

\[
E_{\mathrm{eff}}(x)=\min_a E_{\mathrm{physical}}(x,a).
\]

Divide physical energy by the applied common scale, remove only a constant offset, and compare with original energy. Report centered normalized RMS error, rank correlation, original-minimum rank, and minimum overlap. Separate the full logical-bit domain (exhaustive through 20 original bits, otherwise fixed sampled probes) from valid customer-assignment probes. Slack assignment probes use correct canonical slack and do not cover every possible helper string. No sampled minimum is called a global optimum.

Also report enlarged pair error, unwanted-interaction leakage, validity/convergence, and bounded classical physical endpoint solves. Exact enumeration establishes all minima when feasible. Mixed-integer timeouts remain unproven incumbents; feasible-set bounds are necessary for claims excluding all feasible tied minima. Static checks do not filter otherwise valid quantum inputs.

## Quantum experiment

Use a fixed four-microsecond sinusoidal drive of peak 4 rad/us and linear detuning ramp from -8 rad/us to the per-atom target. Individual fields use a virtual DMM device and are emulator-only. Each pair shares identical serialized geometry, pulse, fields, initial state, logical scale and numerical settings; only the interaction override differs. The geometric arm has no override. The intended arm uses the augmented target at the same scale. These are new pulses, so old cloud numbers are contextual, not matched controls.

State-vector simulation through 20 total atoms, 10 ns timestep. Larger cases use MPS (compressed state approximation) with bond limit 64 and 10 ns steps; every such case gets bond limit 128 and 5 ns steps. Refinement differences must be reported; absence of a significant finite-sample difference is not proof of convergence. The shared 20-atom boundary allows comparison to a state-vector baseline but is not an MPS calibration by itself. An inconclusive refinement leaves conclusions provisional and may justify a separately recorded bounded amendment.

Score original assignment validity, capacity feasibility, original optimal clustering, correct original slack, ancillary conditional validity and their joint outcomes. Decode original bits without repair or postselection. Atom order must be reconstructed from returned labels. Ideal-wire validity and full original slack correctness are different checks. Aggregate per problem; retain each paired result and failures. Report independent-problem count three, not total shots or placements.

## Operational controls

Before scientific submission: independent construction tests; target checks; serialized coefficient/atom-order validation; frozen source/input hashes; local AND cloud two-atom discriminator demonstrating intended override differs from geometric interactions.

Maximum two active jobs from this experiment. Use durable per-job handles and a submission journal. Never automatically retry an uncertain POST. Cloud charges are unavailable from the inspected SDK and are not assumed zero. Failed cloud runs are not scientific zero-success data. Persist progress and raw counts, perform independent rescoring, and generate a result report as jobs finish.

## Prespecified conclusion categories

1. Better logical fidelity and better geometric sampling, relative to matched ideal controls: supports a geometry bottleneck for these interventions.
2. Better fidelity but worse ideal and physical sampling: added-atom dynamics/scale burden can outweigh representation gains.
3. No fidelity improvement: this selective-wire construction failed to provide the needed intervention; it does not refute embedding as a bottleneck.
4. Unresolved simulation accuracy or execution failures: report incomplete evidence rather than a physical conclusion.

Do not infer universal causality from an association across three problems. A fixed pulse does not establish independently tuned best performance.
