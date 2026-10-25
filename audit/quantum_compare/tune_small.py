"""Reproducible single-worker pulse search; frozen target/layout inputs, no cloud.
Original and alternative are retrospective diagnostic formulations, NOT a claim
of deployable penalty learning. Keeps all optimizer-seed winners and cross-arms.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,hashlib,json,pickle,time
from pathlib import Path
import numpy as np
import optuna
from dynamics import DiagonalProblem,Pulse,evolve
from formulations import basis_masks,score_probabilities
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=HERE/'tuning_small';SEEDS=[11,29,47]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,obj):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2,allow_nan=False));tmp.replace(path)
def save_study(path,study):
    tmp=path.with_suffix('.tmp');tmp.write_bytes(pickle.dumps(study));tmp.replace(path)
def load(manifest):
    data=json.loads(manifest.read_text());assert data['complete']
    targets=[]
    for row in data['targets']:
        t=row['target']
        if t['tier']!='S' or t['encoding']!='slack':continue
        assert t['certificate']['valid'] and t['atoms']==14
        path=ROOT/row['geometry_path'];g=np.load(path)
        source=np.load(ROOT/row['target_path'])
        assert np.array_equal(g['h'],source['h']) and np.array_equal(g['J'],source['J'])
        alpha=float(g['alpha']);assert alpha>0 and abs(alpha-row['alpha'])<1e-10
        h=alpha*g['h'];j=alpha*g['J'];u=g['physical_J']
        assert max(abs(h))<=40*np.pi and np.all(u>=0) and np.all(j>=0)
        masks=basis_masks(t,'slack')
        # Direct all-state endpoint certificate repeated after physical scaling.
        obj=DiagonalProblem(h,j);emin=obj.linear+obj.pairs;gs=np.isclose(emin,emin.min(),rtol=0,atol=1e-8*max(alpha,1e-4))
        assert masks['optimal_full_encoding'][gs].all()
        targets.append({'target':t,'id':row['id'],'seed':t['instance_seed'],'variant':t['variant'],'h':h,'j':j,'u':u,'masks':masks,'geometry_hash':digest(path),'target_hash':digest(ROOT/row['target_path']),'problems':{'intended':obj,'geometric':DiagonalProblem(h,u)}})
    assert len(targets)==20 and len({r['seed'] for r in targets})==10
    return sorted(targets,key=lambda x:(x['variant'],x['seed']))
def evaluate(rows,mode,pulse,dt):
    result=[]
    for row in rows:
        x=evolve(row['problems'][mode],pulse,dt)
        result.append(dict(id=row['id'],mode=mode,dt=x['dt'],seconds=x['seconds'],score=score_probabilities(x['probabilities'],row['masks'])))
    return result

def converged(row,mode,pulse):
    previous=evolve(row['problems'][mode],pulse,.005);trail=[]
    for dt in [.0025,.00125,.000625,.0003125]:
        current=evolve(row['problems'][mode],pulse,dt)
        tv=float(abs(current['probabilities']-previous['probabilities']).sum()/2)
        scores=score_probabilities(current['probabilities'],row['masks'])
        trail.append(dict(dt=dt,tv_previous=tv,seconds=current['seconds'],score=scores))
        if tv<.001:return dict(id=row['id'],mode=mode,converged=True,history=trail,score=scores)
        previous=current
    return dict(id=row['id'],mode=mode,converged=False,history=trail,score=scores)

def main(args):
    OUT.mkdir(exist_ok=True);rows=load(args.manifest);seeds=sorted({r['seed'] for r in rows});dev=seeds[:3];validation=seeds[3:5];evaluation=seeds[5:]
    protocol=dict(manifest_hash=digest(args.manifest),development=dev,validation=validation,evaluation=evaluation,retrospective=True,alternative_oracle_informed=True,objective='mean original clustering optimum probability across development instances; no repair; all basis states denominator',trial_budget=args.trials,tpe_seeds=SEEDS,random_seeds=[11],equal_budget='32 trials per optimizer run; three TPE replications versus one random replication per arm/formulation; do not compare pooled TPE best against one random run',search_dt=.01,convergence_TV_gate=.001,versions={'numpy':np.__version__,'optuna':optuna.__version__},source_hashes={p.name:digest(p) for p in [Path(__file__),HERE/'dynamics.py',HERE/'formulations.py']},inputs=[{k:r[k] for k in ['id','geometry_hash','target_hash']} for r in rows])
    if (OUT/'protocol.json').exists():assert json.loads((OUT/'protocol.json').read_text())==protocol,'Frozen protocol changed; new output directory required'
    else:write(OUT/'protocol.json',protocol)
    if args.benchmark:
        results=evaluate([r for r in rows if r['seed'] in dev and r['variant']=='original'],'intended',Pulse(),.01)
        write(OUT/'benchmark.json',results);print(json.dumps(results));return
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    for variant in ['original','alternative']:
      for mode in ['intended','geometric']:
       for method,search_seeds in [('tpe',SEEDS),('random',[11])]:
        for seed in search_seeds:
         name=f'{variant}_{mode}_{method}_{seed}';path=OUT/(name+'.pkl');journal=OUT/(name+'.jsonl')
         if path.exists():study=pickle.loads(path.read_bytes())
         else:
          sampler=optuna.samplers.TPESampler(seed=seed,n_startup_trials=8) if method=='tpe' else optuna.samplers.RandomSampler(seed=seed)
          study=optuna.create_study(direction='maximize',sampler=sampler)
          study.enqueue_trial(dict(duration=4.,omega=4.,initial_detuning=-8.,ramp_power=1.,drive_power=1.))
         development=[r for r in rows if r['variant']==variant and r['seed'] in dev]
         def objective(trial):
          pulse=Pulse(duration=trial.suggest_float('duration',1.,12.,log=True),omega=trial.suggest_float('omega',1.,4*np.pi),initial_detuning=trial.suggest_float('initial_detuning',-40.,-1.),ramp_power=trial.suggest_float('ramp_power',1.,3.),drive_power=trial.suggest_float('drive_power',1.,3.))
          start=time.monotonic();result=evaluate(development,mode,pulse,.01)
          score=float(np.mean([r['score']['optimal'] for r in result]))
          trial.set_user_attr('instances',result);trial.set_user_attr('seconds',time.monotonic()-start)
          return score
         def callback(study,trial):
          save_study(path,study)
          with journal.open('a') as f:f.write(json.dumps(dict(trial=trial.number,score=trial.value,params=trial.params,attributes=trial.user_attrs,state=trial.state.name))+'\n');f.flush()
          print(name,'trial',trial.number,'score',trial.value,'seconds',trial.user_attrs.get('seconds'),flush=True)
         remaining=args.trials-len([t for t in study.trials if t.state==optuna.trial.TrialState.COMPLETE])
         if remaining>0:study.optimize(objective,n_trials=remaining,callbacks=[callback],n_jobs=1)
         # Refine three development finalists, then freeze winner before validation/test.
         winner_path=OUT/(name+'_winner.json')
         if not winner_path.exists():
          top=sorted([t for t in study.trials if t.value is not None],key=lambda t:t.value,reverse=True)[:3];finalists=[]
          for trial in top:
           rr=[converged(row,mode,Pulse(**trial.params)) for row in development]
           finalists.append(dict(trial=trial.number,params=trial.params,mean_optimal=float(np.mean([r['score']['optimal'] for r in rr])),all_converged=all(r['converged'] for r in rr),rows=rr))
          assert all(f['all_converged'] for f in finalists),'Numerical convergence failed; do not select winner'
          winner=max(finalists,key=lambda x:x['mean_optimal'])
          write(winner_path,dict(study=name,variant=variant,trained_mode=mode,method=method,seed=seed,winner=winner,finalists=finalists))
         winner=json.loads(winner_path.read_text())
         for row in [r for r in rows if r['variant']==variant]:
          for test_mode in ['intended','geometric']:
           dest=OUT/(name+'__'+row['id']+'__'+test_mode+'.json')
           if dest.exists():continue
           result=converged(row,test_mode,Pulse(**winner['winner']['params']))
           result.update(study=name,split='development' if row['seed'] in dev else 'validation' if row['seed'] in validation else 'evaluation',pulse=winner['winner']['params'])
           write(dest,result)
         print('STUDY COMPLETE',name,flush=True)
    write(OUT/'complete.json',dict(complete=True,studies=16,trials_per_study=args.trials,manifest_hash=digest(args.manifest)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=HERE/'geometry_manifest.json');p.add_argument('--trials',type=int,default=32);p.add_argument('--benchmark',action='store_true');main(p.parse_args())
