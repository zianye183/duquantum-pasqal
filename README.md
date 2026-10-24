# DuQuantum × Pasqal Challenge

Workspace for the Pasqal analog quantum optimization challenge (neutral atoms, QUBO).

## Environment

Python 3.12 virtual environment in `.venv/`.

```bash
source .venv/bin/activate
jupyter lab            # kernel: "Python (duquantum-pasqal)"
```

| Package | Version | Import as |
|---|---|---|
| pulser (+ pulser-simulation) | 1.9.1 | `pulser`, `pulser_simulation` |
| qoolqit | 1.5.0 | `qoolqit` |
| qubo-solver | 0.9.1 | `qubosolver` |
| emu-sv / emu-mps | 2.10.0 | `emu_sv`, `emu_mps` |
| pasqal-cloud | 0.24.0 | `pasqal_cloud` |

- `requirements.txt`: top-level packages
- `requirements.lock.txt`: exact pinned versions (`pip install -r requirements.lock.txt` to reproduce)

If the organizers provide a pinned environment, use theirs instead.

Cloud/QPU credentials: keep them in `.env` (gitignored), never in notebooks, repos or slides.

## Pre-reading checklist

- [ ] IBM Decision Optimization: Linear Programming notebook
- [ ] Pulser tutorial: Programming with Pulser (single-atom + adiabatic prep)
- [ ] Pulser tutorial: Register and Rydberg-atom interactions
- [ ] Qubo Solver tutorial (first solve)
- [ ] unitaryCON Pasqal QUBO demo notebook
- [ ] Papers: Henriet et al. 2020; Pulser 2022; Glover et al. QUBO tutorial
