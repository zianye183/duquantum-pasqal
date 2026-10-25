"""Independent final artifact recomputation; no dynamics or new observations."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,hashlib,sys
import numpy as np
H=Path(__file__).resolve().parent;Q=H.parent;sys.path.insert(0,str(Q));from formulations import classify_bits
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release=read(H/'deferred_release.json');plan=read(H/'deferred_retry3600_plan.json');assert release['status']=='complete' and release['process_returncode']==0;assert release['plan_sha256']==sha(H/'deferred_retry3600_plan.json');assert release['scheduler_sha256']==sha(H/'deferred_scheduler.py')
for name,expected in release['analysis_source_hashes'].items():assert sha(H/name)==expected
for name,expected in plan['source_hashes'].items():
 p=Q/'ramp_remaining_prepared/M_2002_reduced_original_geometric'/name if name in ['sequence.json','config.json'] else H/name
 assert sha(p)==expected
expected=(H/'worker.py').read_text().replace("out=HERE/'local20_reference'/(name+'_dt'+str(dt))", "out=HERE/'local20_reference'/(name+'_dt'+str(dt)+'_retry3600')");assert expected==(H/'retry3600_worker.py').read_text()
checks=[];arrays={}
for arm,dt,suffix in [('intended',10,''),('geometric',10,''),('intended',5,''),('geometric',5,'_retry3600')]:
 name='M_2002_reduced_original_'+arm;p=H/(name+'_dt'+str(dt)+suffix);status=read(p/'status.json');assert status['status']=='completed';source=Q/'ramp_remaining_prepared'/name
 for f,h in status['source_hashes'].items():assert sha(source/(f+'.json'))==h
 raw=np.load(p/'raw_state.npz')['state'].ravel();stored=np.load(p/'logical_probabilities.npz')['probabilities'];order=status['atom_order'];axes=[order.index(f'q{i}') for i in range(19,-1,-1)];independent=abs(raw.reshape([2]*20).transpose(axes).reshape(-1))**2
 error=float(abs(independent-stored).max());assert error<1e-15
 meta=read(source/'metadata.json');scores={k:0. for k in status['exact_probability_scores']}
 for lo in range(0,len(stored),65536):
  ix=np.arange(lo,min(lo+65536,len(stored)),dtype=np.uint32);bits=((ix[:,None]>>np.arange(20))&1).astype(np.int8);m=classify_bits(bits,meta['target'],'reduced')
  for k in scores:scores[k]+=float(stored[ix][m[k]].sum())
 maxdiff=max(abs(scores[k]-status['exact_probability_scores'][k]) for k in scores);assert maxdiff<1e-12
 arrays[(arm,dt)]=stored;checks.append(dict(arm=arm,dt=dt,raw_to_logical_max_error=error,score_recompute_max_error=maxdiff,norm=float(np.vdot(raw,raw).real),seconds=status['seconds'],source_hashes_verified=True))
comparison={a:float(abs(arrays[a,5]-arrays[a,10]).sum()/2) for a in ['intended','geometric']};assert abs(comparison['intended']-read(H/'comparison.json')['intended_timestep_probability_TV'])<1e-15;assert abs(comparison['geometric']-read(H/'geometric_comparison.json')['probability_TV'])<1e-15
mcplan=read(H/'global_cloud_check_plan.json');assert mcplan['MC_replicates']==2000 and mcplan['per_arm_alpha']==.005;global_result=read(H/'global_cloud_check.json');global_checks=[]
for arm in ['intended','geometric']:
 prob=arrays[arm,5]/arrays[arm,5].sum();saved=np.load(H/(arm+'_global_groups.npz'));selected=np.flatnonzero(prob*20000>=5);assert np.array_equal(selected,saved['logical_indices']);groups=np.r_[prob[selected],prob.sum()-prob[selected].sum()];groups/=groups.sum();assert np.max(abs(groups-saved['probabilities']))<1e-14
 cpath=Q/'ramp_remaining_results'/('M_2002_reduced_original_'+arm);counts=read(cpath/'counts.json');state=read(cpath/'state.json');order=state['result_atom_order'];lookup={int(k):i for i,k in enumerate(selected)};observed=np.zeros(len(groups),dtype=int)
 for word,count in counts.items():idx=sum(int(word[order.index(f'q{i}')])<<i for i in range(20));observed[lookup.get(idx,len(groups)-1)]+=count
 assert np.array_equal(observed,saved['counts']);expected=20000*saved['probabilities'];stat=float(np.sum((observed-expected)**2/expected));rng=np.random.default_rng(mcplan['seeds'][arm]);greater=0
 for _ in range(20):sim=rng.multinomial(20000,saved['probabilities'],size=100);greater+=int(np.count_nonzero(np.sum((sim-expected)**2/expected,axis=1)>=stat))
 reference=next(r for r in global_result['checks'] if r['arm']==arm);assert greater==reference['exceedances'] and abs(stat-reference['pearson_statistic'])<1e-10;global_checks.append(dict(arm=arm,grouping_and_counts_match=True,MC_exceedances_reproduced=greater,tail=(greater+1)/2001))
result=dict(passed=True,source_hashes=release['analysis_source_hashes'],runs=checks,timestep_TV=comparison,global_checks=global_checks,original_timeout_retained=read(H/'M_2002_reduced_original_geometric_dt5/status.json')['status']=='timeout',scope='Artifact/source checks and deterministic scoring/Monte Carlo replay only; no new quantum simulation. Empirical diagnostic agreement is not a universal convergence or rare-tail accuracy certificate.')
(H/'final_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
