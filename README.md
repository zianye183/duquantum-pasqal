# DuQuantum × Pasqal — Track A submission

This is the submission guide for the capacity-constrained clustering study. It supersedes the time-dependent status narrative in [the historical research log](audit/quantum_compare/HISTORICAL_REPORT.md). The final short report and presentation are in [submission](submission). All quantum results are noiseless emulations, not hardware measurements.

**Contribution:** reduced assignment saves atoms, and our workflow using BLaDE improves interaction fit relative to the custom placement we tested. **Failure point:** preserving the constrained problem through its QUBO and atomic representation remains difficult. Soft load balance can change the answer before embedding; geometric interactions can then change the low-energy states and sampling probabilities. A better placement-error score is useful but does not guarantee feasible solutions. BLaDE is an existing method used in our workflow, not a new algorithm we claim to have invented.

## 1. Reproduce the submitted evidence

Run commands from the repository root. Python 3.12 was used. The default verification is offline: it never reads credentials, contacts Pasqal, or submits jobs.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-replay.txt
python reproduce.py
```

This checks the supplied file hashes, regenerates the 20 seeded customer/demand draws and validates their feasibility certificates, independently rescores 303 saved condition references from raw counts, checks all 209 completed primary conditions against the final CSV, reconstructs the completed pulse-tuning aggregation, rescores the historical matched cloud experiments, and independently scores all 18 saved small matched-encoding distributions. The 303 references include reused observations: there are 301 unique measured runs, not 303 independent runs. Outputs go to `reproduction_output/verification.json`. Frozen data are not overwritten.

For a fresh calculation of the three-encoding comparison, install the scientific environment and request simulation explicitly:

```bash
python -m pip install -r requirements.lock.txt
python reproduce.py --simulate
```

The command runs the original frozen study in a temporary copy: three problems, three encodings, two interaction arms. It refits layouts, evolves the states, repeats timestep checks, and compares the new feasible/optimal probabilities with the saved results at absolute tolerance $10^{-4}$. It does not merely replay a summary. The original run took 75.3 seconds on its host; another machine may differ. No cloud account is needed. Numerical libraries and hardware can change fitted layouts and rounding; a failed comparison must be investigated, not silently accepted.

Optional small-reference CPLEX check:

```bash
python -m pip install cplex==22.2.0.1
python reproduce.py --cplex
```

This checks both direct constrained clustering and routing for ten small instances: 20 solves, one thread, seed zero, 30-second limit per solve, zero relative and absolute MIP gaps. The saved original verification records its own CPLEX version. The replay does not replace the saved record. CPLEX availability/license terms are separate from this repository.

### What the commands do not claim

Offline replay does not re-run the historical cloud jobs or prove simulator convergence. Fresh `--simulate` covers the 18 small matched conditions only. The completed 944-trial tuning search is validated and aggregated from its pinned trial and winner records; it is not re-optimized by the default command. Exact medium/large reference proofs and large-state numerical convergence are not re-proven by quick replay. Historical source scripts and serialized inputs are retained for deeper reproduction, with their original limitations. No billing amount is inferred from emulator access.

## 2. Problem and encodings (Track A1)

For customer $i$, vehicle $k$, demand $d_i$, capacity $Q$, and Euclidean pair distance $c_{ij}$, the original problem is

$$\min_x F(x)=\sum_k\sum_{i<j}c_{ij}x_{ik}x_{jk},\qquad \sum_kx_{ik}=1,\qquad L_k=\sum_i d_ix_{ik}\le Q.$$

The clustering objective is not route length. After clustering, each group is routed exactly to obtain the separate CVRP metric. Empty groups are allowed.

**One-hot assignment:** $K$ bits per customer, with $A\sum_i(\sum_kx_{ik}-1)^2$.

**Reduced assignment:** $K-1$ explicit bits and one implicit vehicle. On valid codes, $x_{iK}=1-\sum_{k<K}y_{ik}$. For $K=2$, codes $1,0$ need no assignment penalty. For $K=3$, codes $10,01,00$ use $M a_i b_i$. For $K=4$, codes $100,010,001,000$ use $M(a_ib_i+a_ic_i+b_ic_i)$. The implementation may name the implicit vehicle first; vehicle relabeling leaves the problem unchanged. Linear substitution preserves quadratic degree, with $y^2=y$.

**Capacity slack:**

$$E_{\rm slack}=F+P_{\rm assign}+B\sum_k(L_k+s_k-Q)^2.$$

Nonnegative bounded-binary slack represents spare capacity. Weights are $[1,2,4]$, $[1,2,4,8,5]$, and $[1,2,4,8,15]$ for capacities 7, 20 and 30. Every feasible load can have zero capacity penalty. Assignment and capacity weights above a feasible certificate's objective certify the intended optimum for this nonnegative objective.

**Soft balance:**

$$E_{\rm balance}=F+P_{\rm assign}+\mu\sum_k(L_k-Q)^2.$$

This saves slack atoms but is not an exact encoding of capacity. At capacity 7, loads $(5,5)$ and $(6,4)$ are both feasible but receive penalties $8\mu$ and $10\mu$. Infeasible $(8,2)$ receives $26\mu$ and can still win if the objective compensates. Changing capacity at fixed weight only changes constants on valid assignments.

The new matched comparison uses

$$\mu=\frac{\operatorname{mean}_{i<j}c_{ij}}{2\operatorname{mean}_{i<j}d_id_j}.$$

Its slack weights are $A=B=\lceil F(x^{\rm cert})+1\rceil$. Full one-hot balance uses $A=\lceil F(x^{\rm cert})+\mu\sum_k(L_k^{\rm cert}-Q)^2+1\rceil$; reduced assignment uses the sufficient `m_bound` rule in the frozen source. The certificate uses demands, not the optimal answer. Known optima are used only to score this comparison. Historical pulse-tuning diagnostics that used known answers to construct penalties are explicitly separate.

| Encoding | Small atoms | Medium atoms | Large atoms |
|---|---:|---:|---:|
| Assignment plus capacity slack | 14 | 45 | 80 |
| Full one-hot plus balance | 8 | 30 | 60 |
| Reduced assignment plus balance | 4 | 20 | 45 |

The reduced model saves 71.4%, 55.6%, and 43.8% of atoms relative to slack. A separate 100-instance diagnostic found four problems for which no balance weight recovered the constrained optimum; it is not pooled with the 20-instance benchmark.

## 3. Instance generation and verification (Track A2)

Customer positions are uniform in a $100\times100$ square, depot $(50,50)$. Integer demands are sampled from the ranges below. Seed scanning starts at 2000; exact screening rejects infeasible draws and retains capacity-active cases. This is deliberately a capacity-active benchmark, not an unfiltered random population.

| Tier | Problems | Customers | Vehicles | Capacity | Demand range |
|---|---:|---:|---:|---:|---|
| Small | 10 | 4 | 2 | 7 | 1–4 |
| Medium | 5 | 10 | 3 | 20 | 1–8 |
| Large | 5 | 15 | 4 | 30 | 1–10 |

Small seeds: 2002, 2006, 2012, 2031, 2040, 2042, 2060, 2062, 2063, 2073. Medium: 2002, 2006, 2007, 2017, 2018. Large: 2005, 2011, 2013, 2015, 2017.

Every instance includes a demand-feasible certificate, exact clustering reference and exact CVRP reference. Subset enumeration and dynamic programming provide references; Held–Karp computes exact tours within each subset. Each of the 20 instances has one optimal clustering modulo vehicle relabeling. All ten small clustering and routing costs agree with CPLEX.

$$\rho=\frac{\sum_i d_i}{KQ},\qquad \delta=\frac{\max_i d_i}{Q}.$$

Load-ratio ranges are 0.786–0.929, 0.700–0.900 and 0.733–0.867. Largest-demand ratios are 0.429–0.571, 0.400 and 0.333. The CSV retains per-instance values. Full reference regeneration is exponential and separate from quick certificate checking:

```bash
python audit/scaling/references.py --output reproduction_output/instances_regenerated.json
python audit/scaling/baselines.py --instances audit/scaling/references/instances.json --output reproduction_output/baselines_regenerated.json
```

These commands require NumPy. Regeneration does not use cloud resources. Compare scientific fields rather than wall-clock timestamps.

## 4. Embedding methods and fidelity (Track A3)

Our custom placement minimizes relative pair mismatch with geometry penalties and multiple starts. BLaDE is the stronger tested placement baseline. The preserved `embedding.py` and matched-study snapshot contain both implementations. The comparison is between implementations with different search budgets, not a proof of optimal placement.

$$U_{ij}=\frac{C_6}{\lVert r_i-r_j\rVert^6},\quad \alpha=\frac{\sum_{i<j}U_{ij}J_{ij}}{\sum_{i<j}J_{ij}^2},\quad \epsilon_J=\frac{\lVert U-\alpha J\rVert_F}{\lVert\alpha J\rVert_F}.$$

Only off-diagonal coefficients enter the norm. All interaction tails remain included. Geometry requires minimum separation 5 micrometers and maximum radius 38 micrometers. One global field cannot match arbitrary unequal linear coefficients. Individual-field controls in diagnostic emulations therefore are not claimed hardware implementations.

| Mean BLaDE pair error | Small | Medium | Large |
|---|---:|---:|---:|
| Reduced plus balance | 0.204 | 0.534 | 0.370 |
| Assignment plus slack | 0.497 | 0.993 | 1.201 |

Three layouts per problem; ten small, five medium and five large problems. Geometry averages include preparation failures. These are coefficient errors, not quantum-state fidelities. Medium reduced improves from 1.025 with custom placement to 0.534 with BLaDE; large reduced improves from 1.319 to 0.370.

### Classical isolation of pair distortion

Keep the problem, individual fields and energy scale fixed. Solve the intended energy, then replace only pairs with geometric interactions, then use the actual endpoint fields.

| Encoding | Problems | Layouts | Feasible minimum: intended | Pairs changed | Actual endpoint |
|---|---:|---:|---:|---:|---:|
| Small slack | 10 | 60 | 60 of 60 | 0 of 60 | 1 of 60 |
| Medium reduced | 5 | 10 | 10 of 10 | 0 of 10 | 0 of 10 |
| Medium slack | 5 | 10 | 10 of 10 | 0 of 10 | 0 of 5 available |

Counts refer to layouts, not shots or independent instances. One reduced intended model is already suboptimal under the original objective. Small/20-bit cases use exhaustive checks; 45-bit conclusions use optimization bounds and feasibility certificates. See [classical evidence](audit/fidelity/classical_compare/REPORT.md). For deeper checking, run the preserved enumeration script in a scratch checkout; it writes its verification output:

```bash
OPENBLAS_NUM_THREADS=1 python audit/fidelity/classical_compare/verify_classical.py
```

This is more expensive than replay and does not independently solve every 45-bit case.

## 5. Matched quantum controls and pulses (Track A4)

### Three encoding methods on the same three small problems

Seeds 2002, 2006 and 2012; one BLaDE layout per encoding with placement seed zero. Each pair uses identical initial state, individual fields, energy scale and four-microsecond analytic pulse. Only pair interactions differ. The sine drive peaks at 4 radians/microsecond; detuning moves linearly from −8 to the intended endpoint. Scales can differ between encodings. This pulse is distinct from the main notebook's interpolated global pulse.

| Encoding | Atoms | Feasible exact | Feasible geometry | Optimal exact | Optimal geometry |
|---|---:|---:|---:|---:|---:|
| Capacity slack | 14 | 7.81% | 1.10% | 3.90% | 0.55% |
| Full one-hot balance | 8 | 21.61% | 10.55% | 16.00% | 9.67% |
| Reduced balance | 4 | 36.05% | 24.00% | 29.03% | 16.38% |

These are equal-instance mean state probabilities, not sampled frequencies. Feasible and original-optimal probabilities decrease in all nine matched pairs. All 18 arms pass empirical timestep-halving total variation below $10^{-4}$. Two eight-bit arms also agree with adaptive DOP853. Every bitstring's energy was checked in all nine expansions. Both balance models already have an infeasible intended minimum on one problem. The result supports pair distortion as an important bottleneck, not the sole limitation. [Frozen protocol and per-case evidence](audit/encoding_matched_controls/REPORT.md).

### Historical matched cloud experiment

Same pulse within each pair, 20,000 measurements per condition, one small and one medium instance. Use descriptive penalty names: historical “original” means the baseline penalty rule; historical “alternative” means a known-answer-informed penalty rule, **not a different assignment encoding**.

| Model and penalty rule | Feasible exact → geometry | Optimal clustering exact → geometry |
|---|---|---|
| Small slack, baseline | 5.705% → 1.025% | 2.690% → 0.810% |
| Small slack, known-answer diagnostic | 18.000% → 3.065% | 6.000% → 2.980% |
| Medium reduced, baseline | 37.025% → 4.020% | 0.655% → 0.010% |
| Medium reduced, known-answer diagnostic | 43.965% → 0.305% | 0.525% → 0 observed |
| Medium slack, either penalty rule | 0.010% → 0 observed | 0 observed in both |

The completed local medium refinement yields 36.7942% versus 3.8912% feasibility. Its four full saved distributions and refinement records are included. The 45-atom refinements remain incomplete. Exact interactions are an emulator control, not a realizable arbitrary layout. Zero observed is not zero probability. Source scores are `ramp14_score.json` and `ramp_remaining_score.json`; `reproduce.py` rescores their raw counts.

### Pulse tuning: what helped and what did not

The completed small slack study contains 944 fresh trials, 34 winners and 680 case/interaction evaluations. Each selected pulse trains on three instances, then is evaluated unchanged on two validation and five evaluation instances. These were previously inspected cases: evaluation is retrospective.

Complete-answer success requires an optimal customer assignment **and** correct slack bits. Known-answer-informed diagnostic penalties with intended interactions achieve 11.8–23.7% mean complete success across three search seeds, versus 1.33–2.26% for baseline penalties. Those same tuned pulses with geometric interactions fall below the 0.1% reporting floor; direct geometric tuning reaches at most 0.168%. The floor is not a certified upper bound. Assignment-only tuning reached 41.5–49.4% optimal assignments but only 0.221–7.63% complete answers. Pulse menus also changed, so this is not an isolated causal comparison of tuning objectives. Ideal individual fields, some overlong pulses, oracle penalty construction and finite budgets limit deployment claims.

The repository includes pinned trial journals, selected pulses, per-case evaluations and source files. The offline aggregator verifies all 860 pinned dependencies before combining results. One equally budgeted random-search seed was competitive; it does not establish optimizer superiority. See [completed tuning report](audit/quantum_compare/small_results/REPORT.md). Fresh historical optimization is not provided as a portable one-command claim: source execution has historical output locations and warm-start dependencies. Replay fully reconstructs the reported aggregation without reusing optimizer pickle objects.

## 6. Main benchmark and required metrics

The main global pulse lasts four microseconds. Its interpolated drive rises near zero to the device maximum, holds, and returns near zero; detuning sweeps from negative twice that maximum through zero to the fitted endpoint. Three layouts and 2,000 shots per layout yield 6,000 samples per problem. Small runs use state vectors; larger simulations use MPS bond dimension 64, with selected checks at 128. Noise and modulation are off. Some larger observables disagree under refinement, so numerical convergence is unresolved.

Balanced random assigns nearly equal customer **counts**, not demands. Uniform assigns each customer independently. Both controls use the same problems and sample counts; computation costs differ. No repair or postselection is used.

| Metric | BLaDE reduced | Balanced random | Uniform |
|---|---:|---:|---:|
| Small feasible | 38.63% | 70.11% | 31.21% |
| Small optimal | 28.675% | 29.6967% | 12.72% |
| Medium feasible | 3.6833% | 48.4767% | 19.1333% |
| Medium optimal | 0% | 0.0500% | 0.0067% |
| Large feasible | 0.1633% | 55.3167% | 12.5567% |
| Large optimal | 0% | 0% | 0% |

The final primary ledger has 240 conditions: 209 completed and 31 preparation failures. It includes two successful retries absent from the initial ledger. The submitted CSV uses the **final canonical ledger**; do not substitute `run_metrics.csv`, which preserves initial failures. Across primary, transfer and accuracy studies, 303 condition references correspond to 301 distinct completed observations and 602,000 shots. Studies overlap and their instance counts must not be added as independent samples.

$$\operatorname{gap}(C)=100\frac{C-C^*}{C^*},\qquad \epsilon=0,\qquad \tau_{\rm abs}=10^{-8}.$$

| Reduced BLaDE metric | Small | Medium | Large |
|---|---:|---:|---:|
| Best observed model gap | 0% | 37.66% | 81.90% |
| Best observed CVRP gap | 0% | 4.30% | **16.19%** |
| CVRP-reference hit fraction | 28.6567% | 0% | 0% |

Best gaps are minima across a tier, not means and not necessarily the same shot. The CSV also provides the routing gap of the best-model shot. The earlier report's 24.46% large routing gap omitted a successful retry and is superseded. The feasibility/optimality table already used the final results and is unchanged.

[Results CSV](submission/results_track_a.csv) includes instance, method, placement seed, load and largest-demand ratios, feasibility, both reference-hit rates, atom count, pair error, both gaps, reference status, distinct clustering optima, simulator settings and failure status. Undefined gaps remain blank when no feasible outcome exists; missing measurements are not zero success. Reference-hit probabilities in this CSV are observed shot fractions. Confidence intervals from shots alone cannot account for variation across instances or numerical error.

## 7. Wider experiments and interpretation

[Experiment inventory](submission/experiment_index.csv) and [historical source snapshots](submission/historical_sources) record the earlier surrogate, recursive, transferred-penalty, helper-atom and candidate-selection studies. They explain the design history but are not silently pooled with the matched comparison. Some require known answers for diagnosis, change the original objective, or remain incomplete. The seven-minute deck omits helper atoms at the user's request. Their omission is not a claim that they were never tested.

A separate later BLaDE audit found no feasible minima in 80 pair-only models and 72 available endpoints across five medium problems with repeated settings. This is distinct from the classical table above. Eight endpoints were unavailable. The source snapshot documents that conclusion; quick replay does not rerun those optimization proofs.

Practical lesson: first certify the intended model, then inspect low-energy physical candidates, and only then tune pulses with classical controls retained. Compact encoding and lower pair error are real engineering improvements, but their value must be measured by original-problem feasibility and quality. No quantum advantage, universal encoding failure theorem, or globally optimal placement is claimed.

## 8. Fresh cloud reruns and limits

No cloud submission is part of the default entry point. Historical serialized sequences, emulator configurations, metadata and counts are retained for the matched cloud controls; primary prepared sequences/configurations and geometry metadata are also included. To reproduce the **same scientific condition**, use its saved sequence and numerical configuration, retain the returned atom order, and score every raw shot. Do not replace intended interactions with geometry or global fields with individual fields without declaring a new condition. Quantum shot outcomes are stochastic and cannot be expected to match bit-for-bit.

A fresh cloud rerun requires a valid Pasqal project, credentials supplied outside Git, and confirmation of current service access and pricing. The historical schedulers use local process state and absolute retry paths; they are intentionally not a submission entry point. Do not start them blindly. Cloud job costs were not exposed by the inspected SDK. This repository supports verifiable offline evidence and fresh local small controls; it does **not** claim a tested end-to-end replay of every historical cloud submission on a new account.

## 9. Repository map and review status

- `reproduce.py`: offline verification and optional fresh small simulations/CPLEX checks.
- `requirements-replay.txt`: minimal pinned offline environment; `requirements.lock.txt`: fuller scientific environment.
- `submission/`: final four-page report, brief deck, results CSV, file hashes, review record.
- `audit/scaling/`: generator, certificates, canonical metrics, raw counts, independent scorer and original prepared inputs.
- `audit/encoding_matched_controls/`: frozen three-encoding experiment and all 18 distributions.
- `audit/quantum_compare/`: historical matched cloud evidence, local medium references, completed tuning records.
- `audit/fidelity/classical_compare/`: intended/geometric classical comparisons and source cases.

The review checks published claims against their source cohort, distinguishes instance/layout/shot counts, validates raw outcome scoring and preserves unresolved limitations. It is not a guarantee that every historical exploratory script is portable. The report's requirements are mapped to sections A1–A4 above and the metrics CSV. The complete Git repository submission must still be reviewed by the team before final challenge submission.

**AI disclosure:** Codex assisted with derivations, code, simulation, analysis, documentation and presentation. The team remains responsible for scientific claims and submission. Automated verification does not imply completed human review.

## Development setup

The [original development notes](docs/DEVELOPMENT.md) cover notebooks, environment setup and collaboration tools.
