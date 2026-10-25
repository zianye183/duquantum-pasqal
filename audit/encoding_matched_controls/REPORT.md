# Matched exact/geometric controls across encoding methods

Complete: 3 shared small problems, 3 encodings, 9 BLaDE layouts and 18 simulated distributions. No cloud jobs. Exact probabilities from local noiseless state evolution, not measured shot rates.

## Equal-instance means

| Encoding | Atoms | Feasible exact | Feasible geometric | Optimal exact | Optimal geometric |
|---|---:|---:|---:|---:|---:|
| Assignment + capacity slack | 14 | 7.8128% | 1.0985% | 3.9016% | 0.5476% |
| Full one-hot + balance | 8 | 21.6069% | 10.5518% | 16.0030% | 9.6716% |
| Reduced assignment + balance | 4 | 36.0506% | 24.0008% | 29.0342% | 16.3782% |

## Every case

| Seed | Encoding | Feasible exact | Feasible geometric | Optimal exact | Optimal geometric | Exact minimum feasible / optimal | Geometric minimum feasible / optimal |
|---|---|---:|---:|---:|---:|---|---|
| 2002 | Assignment + capacity slack | 5.7769% | 0.6536% | 2.6980% | 0.0497% | True / True | False / False |
| 2002 | Full one-hot + balance | 15.4440% | 12.9245% | 15.0705% | 11.9437% | True / True | True / True |
| 2002 | Reduced assignment + balance | 35.6473% | 27.3795% | 31.5278% | 14.1284% | True / True | True / True |
| 2006 | Assignment + capacity slack | 8.9052% | 0.2237% | 4.7261% | 0.0904% | True / True | False / False |
| 2006 | Full one-hot + balance | 29.3267% | 4.1415% | 15.6909% | 3.4096% | False / False | False / False |
| 2006 | Reduced assignment + balance | 23.0999% | 15.6900% | 18.5827% | 10.3540% | False / False | True / True |
| 2012 | Assignment + capacity slack | 8.7563% | 2.4183% | 4.2807% | 1.5027% | True / True | False / False |
| 2012 | Full one-hot + balance | 20.0500% | 14.5893% | 17.2475% | 13.6613% | True / True | True / True |
| 2012 | Reduced assignment + balance | 49.4048% | 28.9330% | 36.9922% | 24.6523% | True / True | False / False |

## Validation and limits

All 18 distributions passed empirical step-halving total variation below 0.0001. Independent scoring checks: 18 of 18. Full one-hot, first-case exact and geometric arms also match independent adaptive DOP853 below that threshold. Direct-versus-expanded energies checked over every bitstring for all nine models.

Penalties use no optimal answers. The same three retrospective small problems are used throughout. One fixed BLaDE placement seed per encoding; not a robustness survey. Full one-hot uses a fresh conservative assignment penalty, not the historical eight-atom surrogate tuning. This is a new comparison, not a rerun of historical numerical settings. Individual fields and exact matrix controls are emulator-only. Scales differ across encodings, but are fixed within each exact/geometric pair. No pulse tuning, noise or hardware experiment. Full-state probabilities have no shot confidence interval. Tiny tails are not certified in relative error. Soft balance can have incorrect minima even before geometry.

Started 2026-10-25T10:45:09.323566-04:00; finished 2026-10-25T10:46:24.606927-04:00. Measured elapsed: 75.3 seconds. New cloud spend: zero.

Frozen design: PROTOCOL.md. All values and source hashes: results.json and manifest.json. Saved distributions: per-case NPZ files.
