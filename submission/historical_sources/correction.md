# Nonphysical oracle coefficient correction

This is a static, exhaustive ground-state diagnostic. It adds no atoms, performs no quantum dynamics, and does not describe a realizable atom layout. No coefficients or penalties were retuned.

Three small 14-bit slack instances and all five saved medium 20-bit reduced instances use frozen BLaDE placement zero. The same conversion scale is retained. Every tied minimum is classified; feasibility means decoded assignment and capacity, while correct auxiliary slack is recorded separately.

## Arms

- A: exact target individual fields; progressively correct only pair interactions.
- B: saved shared endpoint field stays fixed; progressively correct only pair interactions.
- C: progressively correct both shared fields and pair interactions toward the exact target.

## All ground states feasible, by correction fraction

| Tier / arm | 0% | 25% | 50% | 75% | 90% | 95% | 99% | 100% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S / A | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 3/3 | 3/3 |
| S / B | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| S / C | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 |
| M / A | 0/5 | 0/5 | 0/5 | 2/5 | 3/5 | 4/5 | 5/5 | 5/5 |
| M / B | 0/5 | 0/5 | 1/5 | 2/5 | 2/5 | 2/5 | 2/5 | 2/5 |
| M / C | 0/5 | 0/5 | 1/5 | 3/5 | 3/5 | 4/5 | 5/5 | 5/5 |

## Original-objective optimality at full correction

| Tier / arm | All ground states feasible | All ground states original-optimal |
|---|---:|---:|
| S / A | 3/3 | 3/3 |
| S / B | 0/3 | 0/3 |
| S / C | 3/3 | 3/3 |
| M / A | 5/5 | 4/5 |
| M / B | 2/5 | 1/5 |
| M / C | 5/5 | 4/5 |

Medium reduced seed 2007 has a previously established formulation error: its exact intended minimum is feasible but suboptimal for the original clustering objective. It is retained, and complete coefficient correction cannot remove that formulation error.

The first successful tested correction fraction is a coarse grid observation, not an exact transition threshold. Feasibility need not be monotonic along the path. Ground-state energies are not sampling probabilities.

Completed 192 exhaustive case/arm/fraction systems in 105.112 measured seconds. Cloud submissions and charges: zero. All input and code hashes are frozen in freeze.json; validation.json records endpoint and independent direct-energy checks.
