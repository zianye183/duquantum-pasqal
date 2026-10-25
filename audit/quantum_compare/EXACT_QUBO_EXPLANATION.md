# Does exact-QUBO quantum emulation guarantee feasible answers?

No. It removes interaction-encoding error, but does not guarantee that the quantum evolution prepares a lowest-energy configuration.

The intended binary energy is

\[
E(x)=c+\sum_i h_i x_i+\sum_{i<j}J_{ij}x_ix_j.
\]

There are three distinct claims:

1. **The formulation is correct:** every global minimizer of this energy satisfies the original constraints (and, separately, optimizes the original objective).
2. **The emulator represents it correctly:** endpoint fields and interactions reproduce this energy, up to one common positive scale and an additive constant.
3. **The pulse solves it:** the final state has enough probability on useful feasible/optimal configurations.

Only the first two are ensured by correct construction and checks. The third depends on the evolution, including pulse shape, duration, energy gaps, and numerical accuracy. Quantum emulation computes the evolution; it does not automatically minimize the final energy. Even a perfectly simulated state can have poor feasible-answer probability.

For a correctly encoded target, preparing a ground state is sufficient for feasibility. Sampling a general final state is not. For a feasible-answer probability \(p\), \(S\) independent shots give probability

\[
P(\text{at least one feasible answer})=1-(1-p)^S.
\]

More shots help only when the pulse gives useful feasible probability; they do not repair a wrong formulation or wrong Hamiltonian. This expression assumes independent samples from a fixed final distribution.

## Existing evidence checked in this worktree

The frozen target manifest contains 40 formulation/problem combinations. All 40 target-array hashes match their saved certificates. Certificate counts are:

| Family | Original correct ground states | Alternative correct ground states |
|---|---:|---:|
| Small slack, 14 bits | 10/10 | 10/10 |
| Medium reduced, 20 bits | 4/5 | 5/5 |
| Medium slack, 45 bits | 5/5 | 5/5 |

Here “correct” requires original-objective optimality as well as feasibility. The one failing original medium reduced formulation has six ground configurations: all six are feasible, but none optimizes the original clustering objective. This is a formulation issue, even before any quantum dynamics or geometric encoding error.

These are existing classical certificates, checked for manifest consistency in this session, not new quantum success results. The 45-bit certificates use a sufficient bound, not exhaustive enumeration of every bitstring. The alternative formulations use known reference answers and are diagnostic; their performance does not establish a transferable tuning rule.

## Required comparison

Compare intended interactions against geometric interactions with the same pulse, starting state, linear controls, conversion scale, and numerical settings. Use direct constraint checks on every output. Also compare independently tuned arms under equal search budgets: a pulse chosen for one Hamiltonian need not be a good pulse for the other.

- Good intended results and poor geometric results under the same pulse support encoding distortion as the cause for that pulse.
- Poor intended results mean the quantum preparation still needs improvement or is difficult for that target; geometric error alone cannot explain them.
- A geometric arm rescued by its own pulse tuning shows that retuning can compensate at least partially, without proving the Hamiltonian is accurate.
- Feasible original assignments with incorrect slack are useful assignment answers, but are not correct full-QUBO configurations. Report both metrics.

## Documentation

[Pasqal EmulationConfig](https://docs.pasqal.com/pulser/apidoc/_autosummary/pulser.backend.EmulationConfig/) documents an explicit interaction matrix that replaces distance-derived pair coefficients. [Pulser's QUBO tutorial](https://pulser.readthedocs.io/en/v1.6.2/tutorials/qubo.html) explains the distinction between encoding the QUBO and preparing its ground state. An emulator-only override is a diagnostic: it does not imply arbitrary interactions can be implemented on the physical device.

Cloud acceptance and matrix deserialization alone do not prove the deployed backend applies the override. The runner must pass a discriminating small-system cloud check before larger comparisons are trusted.
