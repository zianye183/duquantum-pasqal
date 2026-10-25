# Candidate-ordering layout experiment

## Scope and hypotheses

Compare average-energy fitting against candidate-ordering fitting, without known answers in training. The free-helper encoding is a heuristic, not an exact gadget reduction. The question is whether cheaply generated candidate labels improve the physical low-energy ordering, and whether eight free helpers improve it further.

Use three medium original reduced targets: seeds 2002, 2006, 2017. These are the first three seed-sorted previously certified original targets; omit the previously defective 2007 formulation before observing new results. This eligibility decision uses historical verification. It does not make the instances untouched test problems. Do not use the answer-informed alternative penalties from the separate wire study.

Three problems, two helper counts (zero/eight), two objectives and three starts produce 36 local fits. No quantum submissions in this stage. Existing studies retain their frozen inputs and execution policies.

## Input boundary

Sanitize existing problem records into a whitelist: instance specification, original scaled target coefficients, frozen shared physical field, target-scale provenance and interaction constant. Exclude known optimal costs, reference partitions, exhaustive state energies and previous fitted coordinates. Put exact references under an evaluation-only directory. Fitting imports no prior study module that constructs exact states or reads references.

The saved target coefficients already have physical energy units. Do not multiply by target scale again. The field and scale remain fixed throughout the comparison. All logical atoms retain their original decoding.

## Candidate budgets

Prepare independent deterministic train/validation/test pools of requested sizes 768/384/512. For each requested size \(m\), generate \(2m\) uniform binary vectors, \(2m\) random original customer assignments, and \(m\) randomized capacity-feasible greedy attempts. The construction checks capacity but does not use known answers. Use at most \(\min(32,\lfloor m/16\rfloor)\) uniformly selected greedy starts, each with 32 relocation/swap proposals; accept only feasible, strictly cheaper moves. Keep proposed candidates as well as accepted trajectory states.

Select approximately 25% invalid assignment encodings, 25% valid assignment encodings exceeding capacity and 50% feasible states. Spread the feasible selection across five cost strata to retain objective diversity. Deduplicate within and across final splits; if a quota is unavailable, fill from the remaining generated bag and record the shortfall. Do not generate indefinitely until the desired pool appears. Exact labels never influence generation, overlap removal or selection.

Record all complete candidate evaluations, construction failures, proposals, duplicates, retained counts, wall time and process time. Preserve the best feasible candidate over all evaluated candidates, separately from the best retained and best training candidate. The baseline comparison must account for preprocessing used by train, validation and test generation. Exact enumeration after fitting is evaluation cost, not deployable preprocessing.

## Physical layout and equal treatment

Use fresh 6.5-micrometer hexagonal lattice positions with fixed jitter seeds 0, 1 and 2, verified legal before optimization. Both objectives receive identical starting positions for each problem/helper/start. Respect minimum spacing 5 micrometers and radius 38 micrometers. Optimize all coordinates, keep all physical interactions, and retain the shared field. Do not insert an ideal interaction override.

For each logical candidate \(x\), minimize the physical energy over all \(2^m\) helper configurations exactly. Smooth interactions are used for derivatives; finalized coordinates and pair distances follow the six-decimal serialized convention for reported physical checks. Record the smooth-versus-rounded difference.

All fits have a 1,500-iteration limit. Record evaluations, convergence flags, wall/process time and valid candidate selection. Equal iterations are not equal runtime; report both. Maximum two local fitting workers, numerical libraries single-threaded.

## Frozen losses

Let \(T_i\) be the fixed target energy of training state \(i\), \(E_i\) its physical effective energy, and \(s=\max(\operatorname{std}(T),10^{-12})\). The baseline is

\[
L_E=\frac{1}{N s^2}\sum_i\left[(E_i-T_i)-\overline{E-T}\right]^2.
\]

Form at most 4,096 deterministic candidate pairs per family. The feasibility family pairs a feasible candidate \(f\) with an invalid or capacity-infeasible candidate \(b\). The cost family pairs cheaper and dearer feasible candidates \(c,d\), excluding cost differences at most \(10^{-9}\) as numerical ties. Pair seeds are 73001 for training and 73002 for validation. Define

\[
L_F=\operatorname{mean}_{f,b}\left[\max\left(0,1+\frac{E_f-E_b}{s}\right)^2\right],
\]

\[
m_{cd}=\operatorname{clip}\left(\frac{C_d-C_c}{\max C_{\mathrm{train,feas}}-\min C_{\mathrm{train,feas}}},0,0.5\right),
\quad
L_C=\operatorname{mean}_{c,d}\left[\max\left(0,m_{cd}+\frac{E_c-E_d}{s}\right)^2\right].
\]

The ordering objective is \(L_E+0.5L_F+0.5L_C\). An empty family contributes zero without reweighting; zero cost spread produces no strictly cheaper/dearer pairs. No weight or margin tuning after outcomes. Report the original target's own pair violations: retaining its ground optimum does not imply agreement with every original-cost ordering. This arm explicitly prioritizes application constraints/cost ordering and may depart from target energies.

## Selection and independent evaluation

Within each start, choose the legal candidate with lowest training objective. Across the three starts, select by the common validation ordering component \(0.5L_F+0.5L_C\), then validation energy loss, then start index. Validation pairs come only from validation candidates and use training normalization and cost range. Test candidates do not influence selection. Freeze selections before exact evaluation, and report all starts.

Report energy error, both unweighted pair losses, strict pair inversion rates, feasible state counts/cost diversity, and the best original candidate baseline. After selections are immutable, independently enumerate the full 20-bit logical domain and minimize all helpers for the 12 selected layouts. Classify all tied logical minima, original feasibility/optimality, costs and feasible-versus-infeasible and optimal-versus-suboptimal margins. Keep original application correctness separate from target-energy correctness. Global certificates require complete enumeration; sampled tests provide no such claim.

Success means improvement on untouched candidate tests and independently established physical minima, not reduced training loss alone. A classical candidate already reaching the exact optimum is reported plainly; subsequent recovery cannot be claimed as an optimization improvement. This local study establishes no quantum advantage or hardware result.

## Gates and amendments

Independent candidate accounting/decoding checks, no-reference-boundary inspection, physical-energy brute-force checks, both objective derivatives, paired initialization hashes, and legal finalized geometry gate the main run. Preserve input/code hashes and all failed attempts. Fix implementation errors with recorded evidence; do not add outcome-selected starts, cases, loss settings or quantum jobs. Timing is measured, not forecast. All changes to this protocol before launch must be recorded; once launched the scientific scope is frozen.
