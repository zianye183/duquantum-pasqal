"""Predeclared local-probability grouping, independent of observed cloud counts."""
import os
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json
import numpy as np
H=Path(__file__).resolve().parent;Q=H.parent
rows=[]
for arm in ['intended','geometric']:
 name='M_2002_reduced_original_'+arm;local=H/(name+'_dt5'+('_retry3600' if arm=='geometric' else ''));prob=np.load(local/'logical_probabilities.npz')['probabilities'];prob=prob/prob.sum();remote=Q/'ramp_remaining_results'/name;counts=json.loads((remote/'counts.json').read_text());state=json.loads((remote/'state.json').read_text());order=state['result_atom_order'];n=sum(counts.values());selected=np.flatnonzero(n*prob>=5.);rest=np.ones(len(prob),dtype=bool);rest[selected]=False;groups=np.r_[prob[selected],prob[rest].sum()];groups/=groups.sum();lookup={int(k):i for i,k in enumerate(selected)};observed=np.zeros(len(groups),dtype=int)
 for bitstring,count in counts.items():
  idx=sum(int(bitstring[order.index(f'q{i}')])<<i for i in range(20));observed[lookup.get(idx,len(groups)-1)]+=count
 expected=n*groups;stat=float(np.sum((observed-expected)**2/expected));seed=542 if arm=='intended' else 543;rng=np.random.default_rng(seed);exceed=0;replicates=2000
 for batch in range(20):
  mc=rng.multinomial(n,groups,size=100);test=np.sum((mc-expected)**2/expected,axis=1);exceed+=int(np.sum(test>=stat))
 p=(exceed+1)/(replicates+1);rows.append(dict(arm=arm,local_dt_ns=5,shots=n,individual_bins=len(selected),pooled_states=int(rest.sum()),pooled_probability=float(groups[-1]),pooled_observed=int(observed[-1]),pearson_statistic=stat,monte_carlo_replicates=replicates,exceedances=exceed,monte_carlo_upper_tail=p,mc_standard_error=float(np.sqrt(p*(1-p)/(replicates+1))),seed=seed,inconsistent_at_familywise_01=p<.005));np.savez_compressed(H/(arm+'_global_groups.npz'),logical_indices=selected,probabilities=groups,counts=observed)
result=dict(checks=rows,scope='Two whole-distribution diagnostic tests with grouping fixed by fine local probabilities alone. All states expected at least5 shots individually, all remaining states pooled. Pearson statistic calibrated by2000 multinomial replicates; two-test Bonferroni threshold0.005 for familywise0.01. Coarse pooling can conceal rare-tail discrepancies; prior rare-category observations retained. Finite MC uncertainty and local numerical error remain.')
(H/'global_cloud_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
