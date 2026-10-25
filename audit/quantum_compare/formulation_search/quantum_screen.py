"""Frozen 12-pulse equal-menu diagnostic formulation screen on development only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
from scipy.stats import qmc
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent))
from dynamics import Pulse,DiagonalProblem,evolve
from formulations import basis_masks,score_probabilities
import formulation_search as fs
OUT=HERE/'quantum_screen'

def menu():
 OUT.mkdir(exist_ok=True);points=qmc.Sobol(d=5,scramble=True,seed=20261025).random_base2(4)[:11]
 pulses=[{'duration':4.,'omega':4.,'initial_detuning':-8.,'ramp_power':1.,'drive_power':1.}]
 for u in points:pulses.append({'duration':float(np.exp(u[0]*np.log(12.))),'omega':float(1+u[1]*(4*np.pi-1)),'initial_detuning':float(-40+39*u[2]),'ramp_power':float(1+2*u[3]),'drive_power':float(1+2*u[4])})
 design={'seed':20261025,'method':'Baseline plus first11 scrambledSobol points from16-point base2 draw','bounds':{'duration':[1,12],'omega':[1,4*np.pi],'initial_detuning':[-40,-1],'ramp_power':[1,3],'drive_power':[1,3]},'duration_transform':'log uniform','pulses':pulses,'trial_count_per_formulation_and_arm':12,'selection_inputs':'First3 small instances only; objective mean original clustering optimal probability. Formulation menu itself retrospectively selected using correctness acrossallinstances.','retrospective':True,'fine_selection':'Top3 pulses separately per formulation and arm at .005/.0025 with further halving to TV<.001, then pick best; evaluate that same winner on opposite arm on same development cases. No evaluation instances in this pilot.'}
 p=OUT/'pulse_menu.json'
 if p.exists():assert json.loads(p.read_text())==design
 else:fs.write(p,design)
 return design

def prepare_cases(manifest):
 cases=[]
 for row in manifest['rows']:
  target=row['target']
  if target['family']!='S_slack':continue
  assert row['outcome']=='ready' and target['certificate']['status']=='valid'
  geom=row['selected_geometry'];path=ROOT/geom['geometry_path'];assert fs.sha(path)==geom['geometry_hash'];a=np.load(path);h=float(a['alpha'])*a['h'];J=float(a['alpha'])*a['J']
  orig=np.load(ROOT/target['npz_path']);assert np.array_equal(orig['h'],a['h']) and np.array_equal(orig['J'],a['J'])
  cases.append({'id':row['id'],'seed':target['instance_seed'],'rule':target['rule_index'],'masks':basis_masks(target['target'],'slack'),'problems':{'intended':DiagonalProblem(h,J),'geometric':DiagonalProblem(h,a['physical_J'])}})
 return cases

def score_one(case,mode,pulse,dt):
 r=evolve(case['problems'][mode],pulse,dt)
 return r,score_probabilities(r['probabilities'],case['masks'])
def fine(case,mode,pulse):
 initial,_=score_one(case,mode,pulse,.005);history=[]
 for dt in [.0025,.00125,.000625,.0003125]:
  current,score=score_one(case,mode,pulse,dt);tv=float(abs(initial['probabilities']-current['probabilities']).sum()/2)
  history.append({'dt':dt,'tv_previous':tv,'seconds':current['seconds'],'score':score})
  if tv<.001:return {'converged':True,'history':history,'score':score}
  initial=current
 return {'converged':False,'history':history,'score':score}

def main(prepare=False):
 m=menu()
 if prepare:print('Frozen12pulse menu',fs.sha(OUT/'pulse_menu.json'));return
 source=HERE/'transfer_layouts/manifest.json';manifest=json.loads(source.read_text());assert manifest['complete'];cases=prepare_cases(manifest);seeds=sorted({c['seed'] for c in cases})[:3];dev=[c for c in cases if c['seed'] in seeds];rules=sorted({c['rule'] for c in dev});assert len(dev)==9
 protocol={'layout_manifest_hash':fs.sha(source),'pulse_menu_hash':fs.sha(OUT/'pulse_menu.json'),'development_instances':seeds,'rules':rules,'source_hashes':{str(p.relative_to(ROOT)):fs.sha(p) for p in [Path(__file__),HERE.parent/'dynamics.py',HERE.parent/'formulations.py']},'expected_coarse_simulations':216,'equal_pulse_menu_for_all_arms_and_rules':True,'search_dt':.01,'TV_refinement_gate':.001}
 path=OUT/'protocol.json'
 if path.exists():assert json.loads(path.read_text())==protocol
 else:fs.write(path,protocol)
 scores=[]
 for rule in rules:
  selected=[c for c in dev if c['rule']==rule]
  for mode in ['intended','geometric']:
   for index,params in enumerate(m['pulses']):
    rows=[]
    for case in selected:
     p=OUT/(case['id']+'__'+mode+'__pulse'+str(index)+'.json')
     if p.exists():row=json.loads(p.read_text())
     else:
      result,score=score_one(case,mode,Pulse(**params),.01);row={'case':case['id'],'mode':mode,'rule':rule,'pulse_index':index,'params':params,'dt':result['dt'],'seconds':result['seconds'],'score':score};fs.write(p,row)
     rows.append(row)
    record={'rule':rule,'mode':mode,'pulse_index':index,'params':params,'mean_optimal':float(np.mean([r['score']['optimal'] for r in rows])),'rows':rows};scores.append(record)
    fs.write(OUT/'coarse_progress.json',{'expected':72,'returned':len(scores),'rows':scores});print('COARSE',rule,mode,index,record['mean_optimal'],flush=True)
 winners=[]
 for rule in rules:
  selected=[c for c in dev if c['rule']==rule]
  for mode in ['intended','geometric']:
   candidates=sorted([r for r in scores if r['rule']==rule and r['mode']==mode],key=lambda r:-r['mean_optimal'])[:3];finalists=[]
   for candidate in candidates:
    index=candidate['pulse_index'];rr=[]
    for case in selected:
     path=OUT/(case['id']+'__'+mode+'__pulse'+str(index)+'__fine.json')
     if path.exists():r=json.loads(path.read_text())
     else:r={'case':case['id'],'mode':mode,'pulse_index':index,**fine(case,mode,Pulse(**candidate['params']))};fs.write(path,r)
     rr.append(r)
    finalists.append({'pulse_index':index,'params':candidate['params'],'mean_optimal':float(np.mean([r['score']['optimal'] for r in rr])),'all_converged':all(r['converged'] for r in rr),'rows':rr})
   assert all(f['all_converged'] for f in finalists),'No certified selection with nonconverged finalist'
   winner=max(finalists,key=lambda r:r['mean_optimal']);cross=[];other='geometric' if mode=='intended' else 'intended'
   for case in selected:
    path=OUT/(case['id']+'__'+other+'__pulse'+str(winner['pulse_index'])+'__fine.json')
    if path.exists():r=json.loads(path.read_text())
    else:r={'case':case['id'],'mode':other,'pulse_index':winner['pulse_index'],**fine(case,other,Pulse(**winner['params']))};fs.write(path,r)
    cross.append(r)
   result={'rule':rule,'trained_mode':mode,'winner':winner,'finalists':finalists,'matched_other_arm':cross};fs.write(OUT/(f'rule{rule}_{mode}_winner.json'),result);winners.append(result)
   print('WINNER',rule,mode,winner['pulse_index'],winner['mean_optimal'],flush=True)
 best={mode:max([r for r in winners if r['trained_mode']==mode],key=lambda r:r['winner']['mean_optimal']) for mode in ['intended','geometric']}
 fs.write(OUT/'results.json',{'complete':True,'winners':winners,'best_joint_formulation_pulse_per_arm':best,'all_converged':all(r['converged'] for w in winners for r in w['matched_other_arm']),'retrospective_diagnostic':True,'evaluated_only_development':True})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');main(p.parse_args().prepare)
