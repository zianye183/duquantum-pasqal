# Pulse-family limits and a prospective extension gate

The running searches test a bounded pulse family, not every quantum annealing strategy. They must not be reported as a fundamental quantum limit. The first family is

\[
\Omega(s)=\Omega_{\max}\sin^q(\pi s),\qquad
\Delta_i(s)=(1-s^p)\Delta_0-s^p h_i,\qquad s=t/T,
\]

with \(1\le p,q\le3\), \(1\le T\le12\) microseconds, \(1\le\Omega_{\max}\le4\pi\) radians per microsecond, and initial detuning from −40 to −1 radians per microsecond. Interactions are always on. The intended and geometric arms share the same drive, individual controls, and initial state.

This family can delay the detuning sweep and make its late portion steeper. It cannot independently slow the end of that sweep, add an intermediate pause, place a broad drive plateau at a difficult transition, or adapt speed to a small instantaneous gap. Thus low performance may reflect an inadequate path or schedule even when the final intended Hamiltonian is correct. Finite random-search/Optuna budgets also do not establish the optimum within this family.

## Prospective decision gate after the current search finishes

Apply these as triggers to launch a new, separately frozen diagnostic family, not as success/failure claims about quantum computing:

1. A refined winner repeatedly lies in the outer 5% of a continuous search bound across optimizer seeds. Reaching the amplitude ceiling calls for changing shape or duration, not exceeding the device amplitude limit.
2. Across optimizer seeds, the baseline remains unbeaten by more than absolute probability 0.001, after numerical convergence checks, while intended-arm performance remains low.
3. The best intended-arm development mean remains below 50% feasibility or 10% original-optimal probability. These are prospective engineering thresholds for additional investigation, not universal definitions of useful performance.
4. Intended and geometric winners respond very differently to schedule changes, requiring a broader matched-pulse comparison before attributing failure predominantly to embedding.

Some preliminary results were already available when this gate was written. It is a forward decision rule for the unfinished search and must not be represented as a preregistration preceding every observation. Decisions should be made from complete replicated search results and stable numerical estimates, not one lucky seed. The frozen first-stage files must remain unchanged.

## Next family: independently adjustable smooth sweeps

Replace the detuning interpolation with a beta cumulative distribution,

\[
r(s)=I_s(a,b),\qquad
\Delta_i(s)=(1-r(s))\Delta_0-r(s)h_i,
\qquad a,b\ge1.
\]

This includes the linear sweep, delayed sweeps, and smooth end-slowing profiles. For example, \(a=1\) gives

\[
r(s)=1-(1-s)^b,
\]

which has finite initial slope and zero final slope when \(b>1\). Taking both parameters above one gives zero slope at both endpoints. Keep the drive smooth and initially/finally zero; allow separate rise, plateau, and fall fractions, constrained to preserve total duration and nonnegative amplitude. A simpler first extension can keep the existing sinusoidal drive and change only the interpolation, so its effect is identifiable.

A subsequent pause or endpoint-slowdown variant should use a small fixed number of continuous interpolation knots, with monotonic detuning interpolation. Freeze the knot bounds, search budget, optimizer seeds, and development instances before evaluating that extension. Give intended and geometric arms equal budgets and evaluate both arm-specific winners unchanged on the opposite arm. Carry original and new formulation anchors through the comparison. Report the best found result without implying global optimality.

## Physical duration versus virtual diagnostic duration

Check the actual chosen device/channel configuration before calling a sequence hardware-compatible. Amplitude and endpoint-detuning bounds alone are insufficient: also validate duration, clock period, waveform bandwidth/modulation, individual-control construction, and DMM constraints where applicable. Never clip a final detuning silently, because that changes the target problem.

Use two explicitly separate tracks:

- **Device-constrained:** every serialized sequence passes the intended device's checks, and comparisons use the same control implementation and timing convention.
- **Virtual diagnostic:** an emulator permits longer duration or ideal individual fields to test whether the model can work in principle. A fixed duration ladder such as 4, 8, 12, 24, and 48 microseconds can diagnose slow convergence, but values exceeding the device limit must stay labeled virtual. These runs do not establish hardware feasibility or charge/runtime affordability.

Numerical accuracy must be re-established for longer schedules and altered shapes. The current small-system rule compares successive timestep refinements with probability total variation below 0.001. Recheck finalists and matched transfers; normalization alone does not prove correct propagation.

## Optional 14-bit spectral diagnostic

If the intended arm remains poor after the bounded extension, inspect a small number of representative development cases along the chosen path. Sparse low-energy eigensolvers can estimate where the accessible energy gap is small. Refine time sampling around suspected minima and report eigenpair residuals and solver convergence.

Do not identify the final classical gap with the minimum gap during evolution. Also do not interpret a vanishing difference between the lowest two eigenvalues automatically as a hard transition: vehicle-permutation symmetry can create degenerate optimal states or a nearly split pair of symmetry-related states. Account for the initial state's accessible symmetry sector and the final optimal manifold. Report the population in the original optimal bitstrings alongside any gap analysis. A gap plot is a diagnostic, not by itself a prediction of final success probability.
