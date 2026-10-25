# Independent review of classical endpoint comparison

## Interpretation required before solving

Three variants isolate different coefficient changes: intended linear and pair coefficients; intended linear coefficients with geometric pair interactions; actual serialized endpoint linear coefficients with geometric pair interactions. Every variant must retain the same logical bit ordering. These are comparisons of classical diagonal endpoint energies, not predictions of finite-time quantum measurement probabilities.

The physical diagonal energy is

\[
E_{\rm diagonal}(x)=-\sum_i\delta_i x_i+\sum_{i<j}\frac{C_6}{r_{ij}^6}x_ix_j.
\]

The target uses full unordered-pair coefficients, so a full symmetric matrix enters with a factor of one half. A QUBO library that sums both matrix triangles needs half those off-diagonal coefficients. Constants do not affect minimizing states, but energy values and solver relative gaps depend on the chosen offset. Never compare raw minima from different variants as though they were the original clustering objective.

Sampling one saved small textbook sequence gives final drive amplitude \(10^{-9}\) radians per microsecond: effectively zero, but not identically zero. Even when the endpoint drive vanishes, the final evolved state need not equal the endpoint ground state. The original feasibility, clustering optimum, and original-objective gap should be computed independently from each minimizing assignment.

## Solver guarantees and numerical safeguards

[SciPy's official mixed-integer solver documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html) describes status zero as optimal and status one as a time or iteration limit. A limited run with an incumbent does not prove optimality. Preserve status, message, lower objective bound and reported relative gap. A missing incumbent is unknown, not infeasible. These are floating-point solver conclusions, not exact arithmetic certificates.

Binary products can be represented by auxiliary variables with the three inequalities

\[
y_{ij}\le x_i,\quad y_{ij}\le x_j,\quad y_{ij}\ge x_i+x_j-1,
\qquad 0\le y_{ij}\le1.
\]

If the original variables are binary, auxiliary variables may be continuous under these constraints. Independently check rounded binary solutions against the original quadratic expression, integrality residuals and auxiliary consistency. Do not discard small nonzero couplings merely for convenience: many weak edges may collectively change the minimizer. Extreme coefficient ranges warrant scaling and an explicit absolute objective residual check.

Exhaustive small-case enumeration establishes all minimizing bitstrings only within its stated numeric tolerance. Uniform weighting over ground-state ties is a descriptive convention, not a physical sampling distribution. A large-case solver ordinarily returns one incumbent; its feasibility cannot establish that every tied ground state is feasible. Report best-found quality with the solver proof status and distinguish this from all-ground-state statistics.

## Scope

This review introduces no cloud jobs. The frozen manifest covers 168 small cases, all 32 selected medium cases at the first placement seed, and eight first-instance large cases. Large cases are selected diagnostic examples, not independent large-scale generalization evidence. Missing actual endpoint sequences after preparation failure stay unavailable rather than being silently synthesized from requested controls.

## Executed independent verification

Reviewed the extraction source: it restores logical atom order, checks sequence coordinates and device interaction coefficient against the saved pair artifact, samples negative endpoint detunings, and records the remaining drive amplitude. Distances are rounded to six decimals deliberately to match the previously verified Pulser pair-interaction convention; this is distinct from the unrounded descriptive fidelity metric. Constants are explicitly dropped in every variant.

The independent verifier uses full symmetric matrix multiplication and big-endian enumeration, instead of the solving script's pair loop and opposite bit enumeration order. It imports neither solver nor production scoring code. All **504 small case-variant comparisons** agree on the complete minimizing-bitstring set, original feasibility and original optimality. It additionally enumerates all states for six twenty-bit variants: intended, pair-distorted and actual endpoint for both embedding methods on the first medium instance. Every corresponding integer-solver optimum agrees with enumeration; the largest absolute difference is approximately \(7.11\times10^{-14}\).

The small solver was subsequently extended to all ten twenty-bit medium reduced cases. Re-running the independent verifier checks all **534 case-variant results**, including all thirty medium reduced variants. Every minimizing set and feasibility/optimality classification agrees. Across all five medium instances and both embedding methods, every intended minimum is feasible, while every pair-distorted and actual-endpoint model has a unique infeasible minimum. Intended minima achieve original clustering optimality on four of five instances; the fifth is a formulation limitation already present before embedding.

## Primary textbook intended-energy certificates

The separate certificate script independently rebuilds every linear, pair and constant coefficient from the squared assignment/capacity expressions. It constructs an explicit bitstring from each previously proven original optimum partition, including exact nonnegative residual slack for every vehicle. For all 72 primary textbook cases in the manifest, representing 16 distinct problems, the saved intended energy equals

\[
\alpha(f_\star-c).
\]

The original distance expression is nonnegative even on invalid binary assignments. Every violated assignment or capacity equation has nonzero integer residual and therefore costs at least the smaller penalty. The checked strict inequality

\[
\min(A,W)>f_\star
\]

excludes every such state from the ground-state set. The constructed bitstring attains the original optimum with both penalties zero, and positive scaling preserves minimizers. Thus **all intended ground states are feasible and originally optimal** for these primary textbook models. This includes all ten medium textbook cases and both selected large primary textbook cases, even when the generic integer solver times out. The certificate uses the previously proved exact clustering references; it does not assert that the generic solver itself proved optimality.

Other medium/large physical-model incumbents remain subject to their individual time limits and numeric proof status. Evidence and standalone verification scripts are saved beside this review.

## Bounds excluding feasible physical ground states

A separate bounded check minimizes each medium primary textbook physical energy subject only to original customer assignment and capacity requirements. Helper bits remain free; enforcing correct helper values would improperly restrict decoded feasibility. All ten pair-distorted variants and the five available actual-endpoint variants are included, with five seconds allowed per solve. The fifteen solves consumed 30.26 solver seconds; fourteen reported optimality and one reached its time limit.

For each available unconstrained binary witness, its energy is independently recomputed. If the lower bound on every decoded-feasible state's energy exceeds this witness energy by a conservative coefficient-scaled tolerance, no feasible state can be a global minimizer—even when the unconstrained optimum or constrained optimum remains unproved. The saved bound artifact records each comparison; rerunning its script reuses the constrained solves and refreshes comparisons as main solver witnesses arrive.

The constraint builder was separately checked on a real fourteen-bit model against exhaustive decoded-feasible enumeration, leaving helper bits free. Both its lower bound and feasible optimum matched. These large-case certificates remain numerical solver bounds with substantial observed margins, not exact-rational proofs.

After all medium witnesses arrived, **all fifteen comparisons exclude every decoded-feasible ground state**. The smallest separation is 6.33649 energy units, while the largest comparison tolerance is 0.00072848. Even the constrained solve that reached its time limit returned a sufficiently strong lower bound. Combined with the intended-model certificates, this establishes that geometric pair distortion alone destroys ground-state feasibility in all ten selected primary medium textbook fits. The five actual-endpoint variants also lack feasible ground states; the five BLaDE actual endpoints remain unavailable because preparation failed.
