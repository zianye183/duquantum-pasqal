from pathlib import Path
import json
import numpy as np
from scipy.stats import binom
H=Path(__file__).resolve().parent;rows=[]
for p in sorted(H.glob('M*/status.json')):
 r=json.loads(p.read_text())
 if r['status']=='completed':rows.append(dict(id=r['id'],dt_ns=r['dt_ns'],seconds=r['seconds'],norm=r['raw_state_norm'],scores=r['exact_probability_scores']))
result=dict(runs=rows,comparison_available=False)
a=H/'M_2002_reduced_original_intended_dt10';b=H/'M_2002_reduced_original_intended_dt5'
if (b/'logical_probabilities.npz').exists():
 p=np.load(a/'logical_probabilities.npz')['probabilities'];q=np.load(b/'logical_probabilities.npz')['probabilities'];s=json.loads((a/'status.json').read_text());t=json.loads((b/'status.json').read_text());diff={k:t['exact_probability_scores'][k]-s['exact_probability_scores'][k] for k in s['exact_probability_scores']};tail=json.loads((H/'cloud_tail_check.json').read_text());invalid=1-t['exact_probability_scores']['assignment_valid'];examples=[dict(**r,fine_dt_probability=float(q[r['logical_index']])) for r in tail['invalid_bitstrings']]
 result.update(comparison_available=True,intended_timestep_probability_TV=float(abs(p-q).sum()/2),intended_timestep_score_changes=diff,cloud_invalid_examples=examples,fine_dt_invalid_probability=invalid,fine_dt_cloud_count_upper_tail=float(binom.sf(1,20000,invalid)),scope='One halving of timestep on intended arm. No geometric timestep refinement, tensor-network or global convergence guarantee. Cloud rare-tail finding retained without selective resampling.')
(H/'comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
