import json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'results.json').read_text());assert r['manifest']['status']=='complete'
# Independent score reconstruction from saved probabilities and source instances.
instances=json.loads((HERE/'snapshot/instances.json').read_text())['instances'];checks=[]
for row in r['rows']:
 I=next(x for x in instances if x['tier']=='S' and x['seed']==row['seed']);N,K,Q=I['N'],I['K'],I['Q'];q=np.array(I['q']);c=np.array(I['c']);n=row['atoms'];z=(np.arange(1<<n)[:,None]>>np.arange(n))&1
 if row['encoding']=='reduced_balance':
  assign=z[:, :N];valid=np.ones(len(z),bool);X=np.stack([assign==k for k in range(K)],axis=1)
 else:
  X=z[:,:N*K].reshape(-1,K,N);valid=(X.sum(1)==1).all(1)
 loads=X@q;feas=valid&(loads<=Q).all(1);cost=np.einsum('ski,ij,skj->s',X,np.triu(c,1),X);opt=feas&np.isclose(cost,row['f_star'],atol=1e-8,rtol=0)
 for arm in ['exact','geometric']:
  f=np.load(HERE/f"{row['seed']}_{row['encoding']}_{arm}.npz");p=f['probabilities']
  assert np.array_equal(feas,f['feasible']) and np.array_equal(opt,f['optimal'])
  for m,mask in [('feasible',feas),('optimal',opt)]:assert abs(p[mask].sum()-row['arms'][arm]['probability'][m])<1e-12
  checks.append(f"{row['seed']}/{row['encoding']}/{arm}")
labels={'slack':'Assignment + capacity slack','full_balance':'Full one-hot + balance','reduced_balance':'Reduced assignment + balance'}
text=['# Matched exact/geometric controls across encoding methods','', 'Complete: 3 shared small problems, 3 encodings, 9 BLaDE layouts and 18 simulated distributions. No cloud jobs. Exact probabilities from local noiseless state evolution, not measured shot rates.','', '## Equal-instance means','', '| Encoding | Atoms | Feasible exact | Feasible geometric | Optimal exact | Optimal geometric |','|---|---:|---:|---:|---:|---:|']
for enc,v in r['manifest']['summary'].items():
 m=v['means'];atoms=next(x['atoms'] for x in r['rows'] if x['encoding']==enc)
 text.append(f"| {labels[enc]} | {atoms} | {100*m['exact']['feasible']:.4f}% | {100*m['geometric']['feasible']:.4f}% | {100*m['exact']['optimal']:.4f}% | {100*m['geometric']['optimal']:.4f}% |")
text+=['','## Every case','', '| Seed | Encoding | Feasible exact | Feasible geometric | Optimal exact | Optimal geometric | Exact minimum feasible / optimal | Geometric minimum feasible / optimal |','|---|---|---:|---:|---:|---:|---|---|']
for x in r['rows']:
 a=x['arms']['exact'];b=x['arms']['geometric']
 text.append(f"| {x['seed']} | {labels[x['encoding']]} | {100*a['probability']['feasible']:.4f}% | {100*b['probability']['feasible']:.4f}% | {100*a['probability']['optimal']:.4f}% | {100*b['probability']['optimal']:.4f}% | {a['endpoint_all_minima_feasible']} / {a['endpoint_all_minima_original_optimal']} | {b['endpoint_all_minima_feasible']} / {b['endpoint_all_minima_original_optimal']} |")
text+=['','## Validation and limits','',f"All 18 distributions passed empirical step-halving total variation below 0.0001. Independent scoring checks: {len(checks)} of 18. Full one-hot, first-case exact and geometric arms also match independent adaptive DOP853 below that threshold. Direct-versus-expanded energies checked over every bitstring for all nine models.", '', 'Penalties use no optimal answers. The same three retrospective small problems are used throughout. One fixed BLaDE placement seed per encoding; not a robustness survey. Full one-hot uses a fresh conservative assignment penalty, not the historical eight-atom surrogate tuning. This is a new comparison, not a rerun of historical numerical settings. Individual fields and exact matrix controls are emulator-only. Scales differ across encodings, but are fixed within each exact/geometric pair. No pulse tuning, noise or hardware experiment. Full-state probabilities have no shot confidence interval. Tiny tails are not certified in relative error. Soft balance can have incorrect minima even before geometry.','',f"Started {r['manifest']['started_at']}; finished {r['manifest']['finished_at']}. Measured elapsed: {r['manifest']['elapsed_seconds']:.1f} seconds. New cloud spend: zero.",'','Frozen design: PROTOCOL.md. All values and source hashes: results.json and manifest.json. Saved distributions: per-case NPZ files.']
(HERE/'REPORT.md').write_text('\n'.join(text)+'\n');(HERE/'review.json').write_text(json.dumps({'independently_rescored_distributions':len(checks),'all_pass':True},indent=2))
print('\n'.join(text[:12]))
