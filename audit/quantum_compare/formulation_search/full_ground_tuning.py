"""Separate intended-QUBO-ground objective and expanded beta-sweep family.
Preparation is cheap. --run explicitly starts the frozen432-new-trial study.
Twelve previous development pulse points per arm/formulation are shared cached
warm starts, not new trials or independent replications. Frozen prior files stay intact.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import argparse,dataclasses,hashlib,json,pickle,sys,time
from pathlib import Path
import numpy as np
from scipy.special import betainc
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'full_ground_tuning'
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE))
from dynamics import Pulse,DiagonalProblem,evolve
from formulations import score_probabilities
import formulation_search as fs
import quantum_screen as screen
SEEDS=[11,29,47]
@dataclasses.dataclass(frozen=True)
class BetaPulse(Pulse):
    ramp_beta:float=1.
    def validate(self):
        super().validate()
        if not 1<=self.ramp_power<=3 or not 1<=self.ramp_beta<=3:raise ValueError('Beta shapes outside frozenrange')
class BetaProblem(DiagonalProblem):
    def diagonal(self,s,pulse):
        # The b=1 branch is arithmetic-identical to the frozen first family.
        ramp=s**pulse.ramp_power if pulse.ramp_beta==1 else betainc(pulse.ramp_power,pulse.ramp_beta,s)
        return self.pairs+(1-ramp)*(-pulse.initial_detuning)*self.number+ramp*self.linear

def prepare():
 OUT.mkdir(exist_ok=True)
 coarse_path=HERE/'quantum_screen/coarse_progress.json';source=HERE/'transfer_layouts/manifest.json'
 coarse=json.loads(coarse_path.read_text());assert coarse['returned']==72
 protocol={'objective':'mean optimal_full_encoding probability: original intended-QUBO ground-state set, including exact slack equations, acrossfirst3developmentinstances','new_pulse_family':'detuning ramp I_s(a,b), a=ramp_power,b=ramp_beta in[1,3]; sinusoidal powerdriveunchanged. Both objective and family differ from priorsearch.','warm_starts':12,'warm_start_source_hash':fs.sha(coarse_path),'warm_start_policy':'All12existingpoints per formulation/arm copied as completed observations withb=1; samecachedobservations reusedacrossthreeoptimizerseeds. Neithernewquantumexperiments norindependentreplicates.','new_adaptive_trials_per_study':24,'seeds':SEEDS,'formulation_rules':[0,1,24],'arms':['intended','geometric'],'studies':18,'total_new_coarse_trials':432,'total_new_coarse_propagations':1296,'development_instances':[2002,2006,2012],'retrospective_correctness_selected_across_all_instances':True,'layout_manifest_hash':fs.sha(source),'bounds':{'duration':[1.,12.],'omega':[1.,4*np.pi],'initial_detuning':[-40.,-1.],'ramp_power':[1.,3.],'ramp_beta':[1.,3.],'drive_power':[1.,3.]},'duration_log':True,'search_dt':.01,'fine_gate_TV':.001,'finalists_perstudy':3,'refined_winners':'Retainalloptimizerseedwinners; evaluate unchangedwinner onoppositearm. Allsame10smallinstances separateddevelopment3/validation2/evaluation5; nooutcomeoutsidefirst3selectswinners.','reporting':'Alwaysboth clustering-optimal and intended-QUBO-ground probabilities, feasibility, perinstance minimum, and 1-(1-p)^shots underindependentrepeatedpreparations assumption.','virtual_control_warning':'Individualfields idealized; beta family notyet serialized or hardware-validated. T<=12us doesnotestablishdevicedurationcompatibility.','sources':{str(p.relative_to(ROOT)):fs.sha(p) for p in [Path(__file__),HERE.parent/'dynamics.py',HERE.parent/'formulations.py',HERE/'quantum_screen.py']}}
 p=OUT/'protocol.json'
 if p.exists():assert json.loads(p.read_text())==protocol,'Newprotocolcannotoverwriteexistingstudy'
 else:fs.write(p,protocol)
 return protocol,coarse

def loadcases():
 source=json.loads((HERE/'transfer_layouts/manifest.json').read_text());cases=screen.prepare_cases(source)
 for c in cases:
  c['problems']={mode:BetaProblem(p.h,p.J) for mode,p in c['problems'].items()}
 return cases

def evalcase(case,mode,pulse,dt):
 r=evolve(case['problems'][mode],pulse,dt);return r,score_probabilities(r['probabilities'],case['masks'])
def fine(case,mode,pulse):
 prev,_=evalcase(case,mode,pulse,.005);history=[]
 for dt in [.0025,.00125,.000625,.0003125]:
  current,score=evalcase(case,mode,pulse,dt);tv=float(abs(current['probabilities']-prev['probabilities']).sum()/2);history.append({'dt':dt,'tv_previous':tv,'seconds':current['seconds'],'score':score})
  if tv<.001:return {'case':case['id'],'converged':True,'score':score,'history':history}
  prev=current
 return {'case':case['id'],'converged':False,'score':score,'history':history}

def save_pickle(path,study):
 temp=path.with_suffix('.tmp');temp.write_bytes(pickle.dumps(study));temp.replace(path)

def tests():
 from scipy.integrate import solve_ivp
 h=np.array([-1.,-.7,.2,-.4]);J=np.array([[0,1,.3,.2],[1,0,.5,.1],[.3,.5,0,.8],[.2,.1,.8,0.]])
 old=DiagonalProblem(h,J);new=BetaProblem(h,J);base=Pulse(duration=1.3,omega=2.3,initial_detuning=-3,ramp_power=1.2)
 a=evolve(old,base,.01,return_state=True)['state'];b=evolve(new,BetaPulse(**dataclasses.asdict(base)),.01,return_state=True)['state'];assert np.array_equal(a,b)
 pulse=BetaPulse(duration=1.3,omega=2.3,initial_detuning=-3,ramp_power=2.,ramp_beta=3.)
 assert np.array_equal(new.diagonal(0,pulse),new.pairs+3*new.number) and np.array_equal(new.diagonal(1,pulse),new.pairs+new.linear)
 X=np.zeros((16,16))
 for col in range(16):
  for i in range(4):X[col^(1<<i),col]=1
 # Independent beta(2,3) polynomial CDF:6s²-8s³+3s⁴.
 def rhs(t,y):
  s=t/pulse.duration;r=6*s*s-8*s**3+3*s**4
  diag=new.pairs+(1-r)*3*new.number+r*new.linear
  return -1j*(diag*y+pulse.omega*np.sin(np.pi*s)/2*(X@y))
 y=np.zeros(16,complex);y[0]=1;reference=solve_ivp(rhs,[0,pulse.duration],y,method='DOP853',rtol=1e-12,atol=1e-13).y[:,-1]
 errs=[]
 for dt in [.02,.01,.005]:errs.append(float(np.linalg.norm(evolve(new,pulse,dt,return_state=True)['state']-reference)))
 assert errs[0]/errs[1]>3.5 and errs[1]/errs[2]>3.5 and errs[-1]<1e-4
 result={'passed':True,'old_family_b1_bitwise_equal':True,'independent_beta_polynomial_reference_errors':errs,'endpoint_linear_and_pair_terms_correct':True}
 fs.write(OUT/'numerical_tests.json',result);print(json.dumps(result))

def run(protocol,coarse):
 import optuna
 from optuna.distributions import FloatDistribution
 optuna.logging.set_verbosity(optuna.logging.WARNING);cases=loadcases();seeds=sorted({c['seed'] for c in cases});assert seeds[:3]==protocol['development_instances']
 distributions={k:FloatDistribution(*v,log=k=='duration') for k,v in protocol['bounds'].items()}
 for rule in protocol['formulation_rules']:
  current=[c for c in cases if c['rule']==rule];dev=[c for c in current if c['seed'] in seeds[:3]]
  for mode in protocol['arms']:
   for seed in SEEDS:
    name=f'rule{rule}_{mode}_{seed}';sp=OUT/(name+'.pkl')
    if sp.exists():study=pickle.loads(sp.read_bytes())
    else:
     study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=seed,n_startup_trials=12))
     for warm in [r for r in coarse['rows'] if r['rule']==rule and r['mode']==mode]:
      params={**warm['params'],'ramp_beta':1.};value=float(np.mean([r['score']['optimal_full_encoding'] for r in warm['rows']]))
      study.add_trial(optuna.trial.create_trial(params=params,distributions=distributions,value=value,user_attrs={'cached_warm_start':True,'source_pulse_index':warm['pulse_index'],'instances':warm['rows']}))
     save_pickle(sp,study)
    def objective(trial):
     params={k:trial.suggest_float(k,*v,log=k=='duration') for k,v in protocol['bounds'].items()};pulse=BetaPulse(**params);rows=[];start=time.monotonic()
     for case in dev:
      result,score=evalcase(case,mode,pulse,.01);rows.append({'case':case['id'],'score':score,'seconds':result['seconds']})
     trial.set_user_attr('instances',rows);trial.set_user_attr('seconds',time.monotonic()-start);trial.set_user_attr('cached_warm_start',False)
     return float(np.mean([r['score']['optimal_full_encoding'] for r in rows]))
    def callback(study,trial):
     save_pickle(sp,study)
     with (OUT/(name+'.jsonl')).open('a') as f:f.write(json.dumps({'trial':trial.number,'params':trial.params,'value':trial.value,'attributes':trial.user_attrs})+'\n')
     print(name,trial.number,trial.value,trial.user_attrs['seconds'],flush=True)
    fresh=sum(t.state==optuna.trial.TrialState.COMPLETE and not t.user_attrs.get('cached_warm_start',False) for t in study.trials)
    if fresh<24:study.optimize(objective,n_trials=24-fresh,n_jobs=1,callbacks=[callback])
    winner_path=OUT/(name+'_winner.json')
    if not winner_path.exists():
     top=sorted(study.trials,key=lambda t:-t.value)[:3];finalists=[]
     for trial in top:
      rr=[fine(case,mode,BetaPulse(**trial.params)) for case in dev]
      finalists.append({'trial':trial.number,'params':trial.params,'mean_ground_probability':float(np.mean([r['score']['optimal_full_encoding'] for r in rr])),'rows':rr,'all_converged':all(r['converged'] for r in rr)})
     assert all(r['all_converged'] for r in finalists)
     winner=max(finalists,key=lambda r:r['mean_ground_probability']);fs.write(winner_path,{'rule':rule,'mode':mode,'seed':seed,'winner':winner,'finalists':finalists})
    winner=json.loads(winner_path.read_text())['winner']
    for case in current:
     for arm in protocol['arms']:
      p=OUT/(name+'__'+case['id']+'__'+arm+'.json')
      if p.exists():continue
      rr=fine(case,arm,BetaPulse(**winner['params']));rr.update(arm=arm,trained_arm=mode,rule=rule,optimizer_seed=seed,params=winner['params'],split='development' if case['seed'] in seeds[:3] else 'validation' if case['seed'] in seeds[3:5] else 'evaluation')
      for metric in ['optimal','optimal_full_encoding','feasible']:
       probability=rr['score'][metric];rr['p_any_'+metric+'_2000_independent_shots']=float(-np.expm1(2000*np.log1p(-probability))) if probability<1 else 1.
      fs.write(p,rr)
    print('STUDY COMPLETE',name,flush=True)
 fs.write(OUT/'execution_complete.json',{'complete':True,'studies':18,'new_trials':432,'scientific_completion_requires_all_saved_fine_flags_true':True})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--test',action='store_true');args=p.parse_args();protocol,coarse=prepare()
 if args.test:tests()
 elif args.run:run(protocol,coarse)
 else:print(json.dumps({'prepared':True,'new_trials':432,'warm_starts_per_study':12,'runs_started':0}))
