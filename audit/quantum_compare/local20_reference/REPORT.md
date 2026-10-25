# Independent official local twenty-atom reference

The same frozen cloud baseline sequences and interaction configurations were run with the installed official state-vector emulator on one CPU thread. No waveform substitution, layout refit, coefficient change, repair, or postselection was used. Local changes were CPU execution, retention of the final state, and explicitly recorded numerical time steps. All four requested references are now complete. The geometric five-nanosecond reference required a separately authorized retry after its first attempt timed out; that failure remains preserved.

Raw complex states, complete probabilities, sampled counts, source input hashes, package versions and per-run status files are retained. Atom ordering was verified against three explicit official single-excitation states at positions zero, one and nineteen. These confirm occupation bits, register order for raw state indices, and the conversion to logical little-endian ordering. No bit complement is applied.

| Interaction model | Time step | Feasible probability | Optimal probability | Measured run seconds |
|---|---:|---:|---:|---:|
| Intended exact QUBO | 10 ns | 0.3679457448 | 0.0066128191 | 891.14 |
| Geometric | 10 ns | 0.0389132272 | 0.0000114650 | 569.76 |
| Intended exact QUBO | 5 ns | 0.3679419543 | 0.0066125707 | 749.19 |
| Geometric, authorized retry | 5 ns | 0.0389121322 | 0.0000114656 | 596.22 |

For this reduced encoding, complete-encoding feasibility and optimality equal the corresponding columns. Intended-arm time-step halving changes the complete distribution by total variation 0.0000360060, feasibility by -0.00000379047, and optimality by -0.000000248422. This supports numerical stability for these metrics under one refinement; it is not a global convergence guarantee or evidence that the fixed pulse is well tuned.

The intended model still has substantial failure probability even without geometric distortion. Geometry substantially worsens this fixed-pulse example. Neither finding alone describes the achievable result after careful pulse and formulation tuning.

Two cloud rare-event observations are retained. The intended cloud sample contained two assignment-invalid states in 20000 shots versus 0.1836 expected under the local ten-nanosecond distribution. The exact binomial upper tail is 0.01493 (0.01538 under the finer local distribution). The geometric cloud sample contained two optimal states versus 0.2293 expected, giving an upper tail of 0.02260. Actual submitted configurations, serialized sequences and atom ordering match the local sources. These are marginal diagnostic discrepancies, not multiplicity-adjusted discovery claims or proof of backend error. Individual observed states were inspected after seeing the data and do not justify unadjusted state-specific significance claims. No selective resampling was performed.

The initial adaptation mistakenly retained a fourteen-bit shift constant in its new twenty-bit postprocessor. This was caught before any scientific output, the approximately forty-second preliminary attempt was stopped and retained, and the corrected code was restarted. Explicit twenty-bit basis tests subsequently passed. Completed run states use the corrected conversion.

Resource limits: each run is capped at 1200 seconds on the process monotonic clock. Calendar elapsed time can exceed this across host pauses; measured run seconds are not calendar elapsed time or billable cloud time. The official progress logger's memory unit label is unreliable and is not used as a memory estimate. OS observations during the first run showed roughly 300–330 MB resident; this is an observation, not a certified peak. This reviewer submitted no cloud runs.

The first geometric five-nanosecond attempt timed out at 1200.04 monotonic seconds after step 703 of 800, with no final state. A separate retry was authorized before execution, with unchanged scientific inputs and a 3600-second cap, conditional on the original tuning worker exiting. The guarded retry started at 7:15:52 am ET and completed at 7:25:54 am ET on October 25, 2026. Its measured simulation/scoring time was 596.22 seconds. The original timeout, cap-change rationale, release hashes and separate retry artifacts are retained. This resource-driven retry did not change parameters or select a favorable scientific outcome.

## Completed refinement and cloud comparison

Geometric timestep halving changes the full probability distribution by total variation 0.0000247899, feasibility by -0.00000109499, and optimality by 0.00000000055652. Together with the intended comparison, this supports stability under one timestep refinement at the same solver tolerances. It does not certify all propagation error, other pulses or instances, relative rare-event accuracy, or hardware performance.

The predeclared grouped whole-distribution cloud comparison is now complete. Groups were chosen solely from the finer local distributions: states expected at least five counts in 20000 shots individually, all remaining states pooled. Intended interactions produced 650 individual groups plus the pool; geometry produced 477 plus the pool. A Pearson statistic was calibrated by 2000 multinomial replications per arm using the frozen random seeds. The resulting upper tails were 0.71664 and 0.08046, respectively, both above the predeclared per-arm threshold of 0.005. These diagnostics did not detect a broad discrepancy at the chosen grouping and threshold. They do not establish equivalence or certify pooled rare tails. Monte Carlo standard errors are approximately 0.0101 and 0.0061.

The previously observed rare-category discrepancies remain: the finer intended distribution gives an upper-tail probability of 0.01538 for at least two assignment-invalid cloud shots, and the finer geometric distribution gives 0.02260 for at least two optimal cloud shots. No selective resampling erased these observations. The coarse grouping can hide such behavior and is explicitly reported alongside it.

Independent final verification checked all input/release/source hashes, reconstructed all four logical distributions directly from raw states using tensor-axis permutation, and rescored every basis state in bounded chunks. Probability conversion matched exactly; score discrepancies were at most 0.000000000000000111. Both timestep total variations and the frozen Monte Carlo grouping, observed counts and exceedance counts reproduced exactly. See final_verification.json and COMPLETION_SUMMARY.json. No new quantum simulation was used for this final verification. No local reference process remains running.
