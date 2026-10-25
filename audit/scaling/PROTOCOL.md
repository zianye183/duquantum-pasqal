# Frozen scaling study

Created October 24, 2026 before outcome inspection. Extends the earlier audit; does not claim its tuned single-instance result generalizes.

## Objective and requirements

Compare custom and Pasqal BLaDE placement across independent generated instances and placement seeds, including medium and large sizes. Produce graphics for feasibility, original optimal clustering, coupling density, embedding fidelity, best gaps, atom counts and reference status. Keep all intended conditions, including failures, in the experiment ledger. Analyze partial results as they arrive; no outcome-based seed replacement.

## Primary matrix

- First 10 small, 5 medium and 5 large feasible capacity-active instances with seed search starting at 2000. Reject only mathematical infeasibility or inactive capacity, before physical results.
- Small: 4 customers, 2 vehicles, capacity 7. Medium: 10 customers, 3 vehicles, capacity 20. Large: 15 customers, 4 vehicles, capacity 30. Demand bounds follow the challenge's established generators.
- Two encodings: textbook assignment plus bounded binary slack (14/45/80 atoms); reduced assignment plus equal-weight load balancing (4/20/45 atoms).
- Two placement methods: custom relative-interaction-error optimization, and Pasqal BLaDE. Three independent placement seeds: 0, 1, 2.
- Primary total: 240 conditions. Same four-microsecond global pulse policy and 2,000 shots per condition. Isolates placement under a shared pulse; does not compare each library's default pulse.
- Custom computational budget: eight starts, 3,000 optimization iterations each, analytic gradient checked against finite differences. The prelaunch synthetic checks showed 300 iterations commonly failed to converge, so this was increased before scientific outcomes were inspected. BLaDE MDS also receives the 3,000-iteration cap; other settings recorded explicitly. Placement time and convergence recorded; no claim of equal compute budget.
- Textbook penalties: both equal to the ceiling of a feasible certificate's cost plus one. Reduced balance coefficient uses equal mean objective/balance coupling contributions; never selects using the reference optimum.
- Exact references are evaluation-only. They never guide embedding, pulse, or the primary parameter choice.

## Accuracy and execution

State-vector cloud simulation for at most 20 atoms. Matrix-product-state cloud simulation for 45 and 80 atoms, initially maximum bond dimension 64. The latter compresses the quantum state and is approximate. Prespecified validation: compare to state-vector on the first medium reduced condition for both embedders, and double bond dimension on the first medium slack and first large condition of each encoding for both embedders. Report discrepancies and do not claim convergence from agreement of one metric alone. Retain raw distributions; deterministic state-vector repetitions merely for different measurement seeds are not treated as independent instances.

Initially use four new concurrent remote jobs. After verifying all first four were running normally, increase to eight total with a four-MPS cap, so large simulations cannot block small state-vector controls. The observer may restart with persisted batch handles to apply scheduling changes; cloud jobs are not restarted. Save prepared sequences/configurations and input hashes before submitting. Persist batch identifiers immediately. Resume by querying existing jobs; never resubmit merely because polling timed out. No exact-interaction overrides in primary results. No classical repair/postprocessing of quantum samples.

## Metrics

Decoded feasibility means exactly one assignment per customer and every load within capacity. Also report exact slack equalities for the textbook encoding, so decoded success cannot be confused with exact encoded constraint satisfaction. Reduced invalid codes count as failures.

Optimal-clustering rate uses the original constrained clustering objective with zero requested gap, up to a stated numerical comparison tolerance; truck permutations count as the same clustering. Best gaps are undefined when no feasible shot exists, not zero. Report original clustering and routed full-routing reference gaps separately, and distinguish the route of the best-clustering shot from the independently best routed shot.

Embedding relative error is the norm of realized off-diagonal interactions minus scaled target interactions, divided by the norm of scaled target interactions. Record scale, linear-field error, unwanted interactions on target-zero pairs, and minimum separation/radius. Target coupling density counts nonzero target pairs; realized interactions are mathematically dense, with effective density additionally reported at one percent of the strongest interaction. This threshold is descriptive, not a claim that smaller interactions vanish.

Aggregate first within each instance across placement seeds, then across independent instances. Show individual-instance distributions and uncertainty, not pooled-shot confidence masquerading as problem-level generalization. Separate conditional completed-run metrics from requested-pipeline success accounting. Freeze all modifications and disclose adaptive followups separately.

## Transferred-penalty generalization cohort

Frozen before inspecting new quantum outcomes: first six small, three medium and three large accepted instances; slack encoding; both embedders; placement seeds zero and one; global and individual atom controls. This adds 96 primary transferred conditions. Individual controls are explicitly emulator-only. Given the independent feasible certificate bound, multiply it by the ratios of the earlier tuned assignment and capacity weights to the earlier bound: respectively 96.54622677434772/168 and 1.3614277128250407/168. This transfers the earlier single-instance method without using the new known answers. It has no general exact-constraint guarantee and never replaces the safe-penalty benchmark.

Add six accuracy checks: first large slack instance, both embedders and both controls at doubled bond dimension; first medium reduced instance, both embedders using MPS64 matched against the primary state-vector condition. Report transferred results separately; no test-outcome-based retuning.

## Completion gates

Every primary condition has a terminal status and retained evidence; medium and large conditions actually attempted on the chosen simulator; selected accuracy comparisons complete or limitations explicitly evidenced; raw counts independently rescored; figures rendered and inspected; report includes all image-requested metrics and uncertainty; spending reported as unknown if the provider does not expose charges. A transient job wait is not completion.

## Accuracy deduplication amendment

Before submitting the two transferred medium reduced accuracy references, verified that they duplicate the corresponding primary medium reduced MPS64 checks. Scientific sequences and configurations are identical. Observable identifiers differ; one serialized sequence also omits library-version metadata, which has no physical effect. Original prepared files are retained unchanged, with exact hashes and equivalence evidence in `transferred_prepared/ALIASES.json`.

The study therefore retains **14 accuracy ledger references but only 12 unique accuracy checks**. The two transferred medium references reuse the corresponding primary result. They receive no additional remote submissions, shots, or independent statistical weight. Family-wise accuracy comparisons use the unique-check count, and reports label reused results explicitly. This amendment changes execution duplication only; no scientific outcome or tuning choice is changed.

## Independence clarification

The fixed generator reuses three seed values across size tiers: twenty distinct instances use seventeen distinct seed values. Coordinates can share prefixes across sizes. Independence claims and bootstrap resampling apply within each tier (ten small, five medium, five large instances), not to a pooled twenty-instance sample. This clarification does not replace instances or change results after inspection.

## Scheduling-only capacity reuse amendment

After the transferred-condition queue is fully terminal and its observer has exited and released its lock, the primary observer may be cooperatively restarted once with a maximum of sixteen submitted jobs and twelve matrix-product-state jobs. This reuses the two observers' existing combined ceilings (eight total/four compressed-state jobs for primary plus eight total/eight compressed-state jobs for transfer). It does not increase those aggregate ceilings, change any condition, input, measurement budget, or scientific selection rule, or add experiments. The gate also requires no uncertain submissions and no separate retry runner still active. Existing provider handles must be resumed, never resubmitted. Before the gate is satisfied the current primary limits remain unchanged.

This is a scheduling change intended to avoid idle slots after one queue drains. Provider charges are unavailable, so unchanged condition counts must not be described as a proven dollar-neutral change. The amendment was recorded at 11:12 pm ET on October 24, 2026, while both queues remained active.
