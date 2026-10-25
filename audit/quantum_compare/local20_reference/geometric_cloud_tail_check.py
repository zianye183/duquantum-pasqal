import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy.stats import binom
H=Path(__file__).resolve().parent;Q=H.parent;sys.path.insert(0,str(Q));from formulations import classify_bits
name='M_2002_reduced_original_geometric';c=Q/'ramp_remaining_results'/name;p=Q/'ramp_remaining_prepared'/name;l=H/(name+'_dt10');state=json.loads((c/'state.json').read_text());meta=json.loads((p/'metadata.json').read_text());counts=json.loads((c/'counts.json').read_text());order=state['result_atom_order'];bits=np.array([[int(k[order.index(f'q{i}')]) for i in range(20)] for k in counts],dtype=np.int8);m=classify_bits(bits,meta['target'],'reduced');probs=np.load(l/'logical_probabilities.npz')['probabilities'];bad=[]
for b,key,valid in zip(bits,counts,m['optimal']):
 if valid:
  idx=int(np.sum(b.astype(np.uint32)<<np.arange(20,dtype=np.uint32)));bad.append(dict(bitstring=key,count=counts[key],logical_index=idx,local_probability=float(probs[idx])))
stat=json.loads((l/'status.json').read_text());pbad=stat['exact_probability_scores']['optimal'];total=sum(counts.values());nbad=sum(x['count'] for x in bad)
checks={}
for field in ['sequence','config']:
 a=json.loads((c/('submitted_'+field+'.json')).read_text());b=json.loads((p/(field+'.json')).read_text());checks[field+'_json_identical']=a==b
assert all(checks.values());result=dict(identity_checks=checks,atom_order_equal=order==stat['atom_order'],optimal_bitstrings=bad,observed_optimal=nbad,shots=total,local_optimal_probability=pbad,expected_optimal_shots=total*pbad,exact_binomial_upper_tail=float(binom.sf(nbad-1,total,pbad)),interpretation='Retain marginal discrepancy. Tail calculation conditional on fixed local dt10 distribution; not a simultaneous test and not a proof of backend inequivalence. No selective resampling.')
(H/'geometric_cloud_tail_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
