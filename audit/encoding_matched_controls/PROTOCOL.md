# Matched encoding controls — frozen before execution

Prompt: Don't use "alternative weights". It is pretty confusing. Do we have the same experiments but for our alternative encoding methods? If not, do it now

Question: Does replacing intended pair interactions with BLaDE geometric pairs reduce feasibility and original optimality across the three encoding families?

Scope: first three small cases in the existing scaling benchmark, seeds 2002, 2006, 2012. All three encodings on each case: one-hot + capacity slack (14 bits), full one-hot + balance (8 bits), reduced assignment + balance (4 bits). Retrospective small-instance diagnostic, no new medium/large claims.

Penalties: slack assignment and capacity weights ceil(F(demand-feasible certificate)+1); balance mu from mean distance / twice mean demand product, with no optimum used. Full one-hot assignment penalty ceil(F(certificate)+mu*sum((certificate loads-Q)^2)+1) gives a feasible energy witness below any assignment-violating state. Reduced assignment penalty uses existing sufficient m_bound. Optimum used only for scoring. Full assignment model is a fresh independently expanded implementation of the same soft-balance energy, not reuse of historical surrogate tuned settings.

Layout: one BLaDE layout per case/encoding, fixed placement seed 0, MDS maxiter 300 and 200 steps per round. Preserve invalid geometry as failure, no result-based reselection. Existing physical scaling makes minimum distance and endpoint fields legal; this does not establish whole hardware sequence compatibility.

Dynamics: local noiseless full-state simulation. Fixed analytic 4-us sine drive peak 4 rad/us; detuning linearly moves from -8 rad/us to exact individual endpoint fields. Only pair matrix changes within a pair. Exact arm alpha*J, geometric arm C6/r^6. Fields alpha*h and scale identical within each pair, but differ across encodings. No cloud jobs, no shots, no repair. This pulse family differs from the historical interpolated notebook pulse; retain study separation.

Numerics: Strang midpoint integration at dt 0.01 and 0.005 us; halve further through 0.0003125 until total variation below 0.0001 for both arms independently. Save full probabilities. Mark unrefined results if gate fails. This is empirical absolute convergence, not relative accuracy on tiny probabilities. Independently verify at least one 8-bit exact/geometric pair using adaptive DOP853 and TV < 0.0001.

Validation: independent direct energy expansion on every bitstring; exact feasible clustering enumeration; all endpoint minima scored. Report all three cases and equal-instance means, no best-case selection. These nine layouts are not nine independent problems. No assertion that exact interactions remove all bottlenecks.
