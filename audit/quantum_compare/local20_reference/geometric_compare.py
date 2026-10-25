from pathlib import Path
import json
import numpy as np
from scipy.stats import binom
H=Path(__file__).resolve().parent;a=H/'M_2002_reduced_original_geometric_dt10';b=H/'M_2002_reduced_original_geometric_dt5';p=np.load(a/'logical_probabilities.npz')['probabilities'];q=np.load(b/'logical_probabilities.npz')['probabilities'];s=json.loads((a/'status.json').read_text());t=json.loads((b/'status.json').read_text());diff={k:t['exact_probability_scores'][k]-s['exact_probability_scores'][k] for k in s['exact_probability_scores']};tail=json.loads((H/'geometric_cloud_tail_check.json').read_text());opt=t['exact_probability_scores']['optimal'];examples=[dict(**r,fine_dt_probability=float(q[r['logical_index']])) for r in tail['optimal_bitstrings']]
r=dict(probability_TV=float(abs(p-q).sum()/2),score_changes=diff,coarse_scores=s['exact_probability_scores'],fine_scores=t['exact_probability_scores'],fine_seconds=t['seconds'],cloud_optimal_examples=examples,fine_dt_cloud_count_upper_tail=float(binom.sf(1,20000,opt)),scope='One timestep halving at unchanged official solver tolerances, not universal convergence certification. Cloud rare finding retained.')
(H/'geometric_comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
