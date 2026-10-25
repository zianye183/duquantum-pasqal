"""Read-only aggregation of frozen small studies. No propagation or selection."""
from pathlib import Path
import argparse,hashlib,json,math,statistics
METRICS=('feasible','optimal','full_encoding_feasible','optimal_full_encoding')
SEEDS=(11,29,47)
Q=Path(__file__).resolve().parent.parent

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def score_valid(row,gate):
 if row.get('converged') is not True:return False
 history=row.get('history',[])
 if not history or not math.isfinite(history[-1].get('tv_previous',float('nan'))) or not 0<=history[-1]['tv_previous']<gate:return False
 for k in METRICS:
  v=row.get('score',{}).get(k)
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1+1e-6:return False
  if history[-1].get('score',{}).get(k)!=v:return False
 norm=row.get('score',{}).get('normalization_error')
 if not isinstance(norm,(int,float)) or not math.isfinite(norm) or abs(norm)>1e-6:return False
 p=row['score'];eps=1e-8
 if p['optimal']>p['feasible']+eps or p['full_encoding_feasible']>p['feasible']+eps or p['optimal_full_encoding']>min(p['optimal'],p['full_encoding_feasible'])+eps:return False
 if 'assignment_valid' in p and (not math.isfinite(p['assignment_valid']) or p['feasible']>p['assignment_valid']+eps):return False
 return True

def inspect(root=Q):
 root=Path(root);repo=root.parents[1];errors=[];studies=[];snapshots={};coverage={}
 def pin(p,expected=None):
  if not p.exists():errors.append('Missing '+str(p));return
  actual=sha(p);snapshots[str(p.relative_to(root)) if p.is_relative_to(root) else str(p)]=actual
  if expected is not None and actual!=expected:errors.append('Hash mismatch '+str(p))
 for family,folder,objective in [('assignment',root/'tuning_small','optimal'),('full_encoding',root/'formulation_search/full_ground_tuning','optimal_full_encoding')]:
  pp=folder/'protocol.json'
  if not pp.exists():errors.append('Missing protocol '+family);coverage[family]={'expected_studies':16 if family=='assignment' else 18,'winners':0};continue
  protocol=read(pp);pin(pp)
  if family=='assignment':
   if protocol.get('trial_budget')!=32 or protocol.get('tpe_seeds')!=list(SEEDS) or protocol.get('random_seeds')!=[11]:errors.append('Unexpected assignment budget')
   for name,h in protocol['source_hashes'].items():pin(root/name,h)
   manifests=[p for p in root.glob('*geometry_manifest.json') if sha(p)==protocol.get('manifest_hash')]
   if len(manifests)!=1:errors.append('Missing unique frozen assignment geometry manifest');manifest_rows={}
   else:
    pin(manifests[0],protocol['manifest_hash']);manifest_rows={r['id']:r for r in read(manifests[0])['targets']}
   cases=[]
   import re
   for item in protocol['inputs']:
    match=re.fullmatch(r'S_(\d+)_slack_(original|alternative)',item['id'])
    if not match:errors.append('Unexpected assignment case '+item['id']);continue
    cases.append({'id':item['id'],'seed':int(match[1]),'formulation':match[2]})
    if item['id'] not in manifest_rows:errors.append('Missing manifest target '+item['id'])
    else:
     mr=manifest_rows[item['id']];pin(repo/mr['geometry_path'],item['geometry_hash']);pin(repo/mr['target_path'],item['target_hash'])
   split={s:k for k in ['development','validation','evaluation'] for s in protocol[k]}
   if [len(protocol[k]) for k in ['development','validation','evaluation']]!=[3,2,5] or len(split)!=10:errors.append('Assignment split mismatch')
   expected=[(f'{v}_{a}_{m}_{s}',v,a,m,s) for v in ['original','alternative'] for a in ['intended','geometric'] for m,ss in [('tpe',SEEDS),('random',[11])] for s in ss]
   marker=folder/'complete.json';trials=32;gate=protocol['convergence_TV_gate']
  else:
   if protocol.get('new_adaptive_trials_per_study')!=24 or protocol.get('warm_starts')!=12 or protocol.get('seeds')!=list(SEEDS) or protocol.get('formulation_rules')!=[0,1,24]:errors.append('Unexpected ground budget')
   for name,h in protocol['sources'].items():pin(repo/name,h)
   layout=root/'formulation_search/transfer_layouts/manifest.json';pin(layout,protocol['layout_manifest_hash']);pin(root/'formulation_search/quantum_screen/coarse_progress.json',protocol['warm_start_source_hash'])
   for r in read(layout)['rows']:
    if r['target']['family']!='S_slack':continue
    pin(repo/r['selected_geometry']['geometry_path'],r['selected_geometry']['geometry_hash']);pin(repo/r['target']['npz_path'],r['target']['npz_hash'])
   coarse=read(root/'formulation_search/quantum_screen/coarse_progress.json')
   if coarse.get('returned')!=72:errors.append('Incomplete cached warm-start source')
   for rule in [0,1,24]:
    for arm in ['intended','geometric']:
     warm=[r for r in coarse.get('rows',[]) if r['rule']==rule and r['mode']==arm]
     if len(warm)!=12 or {r['pulse_index'] for r in warm}!=set(range(12)):errors.append('Incomplete cached warm-start group')
   cases=[{'id':r['id'],'seed':r['target']['instance_seed'],'formulation':'rule'+str(r['target']['rule_index'])} for r in read(layout)['rows'] if r['target']['family']=='S_slack']
   seeds=sorted({r['seed'] for r in cases});split={s:'development' if i<3 else 'validation' if i<5 else 'evaluation' for i,s in enumerate(seeds)}
   if len(seeds)!=10 or seeds[:3]!=protocol['development_instances']:errors.append('Ground split mismatch')
   expected=[(f'rule{v}_{a}_{s}','rule'+str(v),a,'tpe',s) for v in [0,1,24] for a in ['intended','geometric'] for s in SEEDS]
   marker=folder/'execution_complete.json';trials=24;gate=protocol['fine_gate_TV']
  if len({c['id'] for c in cases})!=len(cases):errors.append('Duplicate cases '+family)
  marker_ok=marker.exists() and read(marker).get('complete') is True
  if not marker_ok:errors.append('Missing completion marker '+family)
  else:
   pin(marker);m=read(marker)
   if m.get('studies')!=len(expected):errors.append('Completion study count '+family)
   if family=='assignment' and (m.get('trials_per_study')!=32 or m.get('manifest_hash')!=protocol.get('manifest_hash')):errors.append('Completion trial count '+family)
   if family=='full_encoding' and m.get('new_trials')!=432:errors.append('Completion fresh trial count '+family)
  counts={'expected_studies':len(expected),'winners':0,'expected_case_arm_rows':len(expected)*20,'case_arm_rows':0,'converged_rows':0,'completion_marker':marker_ok,'completed_fresh_trials':0}
  for name,form,arm,method,seed in expected:
   journal=folder/(name+'.jsonl');entries=[]
   if journal.exists():
    pin(journal)
    for line in journal.read_text().splitlines():
     try:entries.append(json.loads(line))
     except json.JSONDecodeError:errors.append('Incomplete trial journal '+name)
   complete=[e for e in entries if family=='full_encoding' or e.get('state')=='COMPLETE']
   counts['completed_fresh_trials']+=len(complete)
   if len(complete)!=trials or {e['trial'] for e in complete}!=set(range(32) if family=='assignment' else range(12,36)) or len({e['trial'] for e in entries})!=len(entries):errors.append('Trial budget/duplicate trial '+name)
   if family=='full_encoding' and any(e.get('attributes',{}).get('cached_warm_start') is not False for e in complete):errors.append('Fresh trial mislabeled '+name)
   selected=[c for c in cases if c['formulation']==form]
   if len(selected)!=10:errors.append('Case count '+name)
   wp=folder/(name+'_winner.json');winner=None
   if wp.exists():
    pin(wp);w=read(wp);winner=w['winner'];counts['winners']+=1
    finalists=w.get('finalists',[])
    dev_ids={c['id'] for c in selected if split.get(c['seed'])=='development'}
    for f in finalists:
     ids=[r.get('id',r.get('case')) for r in f.get('rows',[])]
     if len(ids)!=3 or len(set(ids))!=3 or set(ids)!=dev_ids:errors.append('Finalist development identities '+name)
    if len(finalists)!=3 or any(f.get('all_converged') is not True or len(f.get('rows',[]))!=3 or any(not score_valid(r,gate) for r in f['rows']) for f in finalists):errors.append('Finalist convergence '+name)
    if not any(canonical(f)==canonical(winner) for f in finalists):errors.append('Winner not finalist '+name)
    mean_key='mean_optimal' if family=='assignment' else 'mean_ground_probability'
    if finalists and any(abs(f.get(mean_key,float('inf'))-statistics.mean(r['score'][objective] for r in f['rows']))>1e-10 for f in finalists):errors.append('Finalist objective mismatch '+name)
    if finalists and winner.get(mean_key)!=max(f.get(mean_key) for f in finalists):errors.append('Winner not best refined finalist '+name)
    if family=='assignment' and any(w.get(k)!=v for k,v in [('study',name),('variant',form),('trained_mode',arm),('method',method),('seed',seed)]):errors.append('Winner metadata mismatch '+name)
    if family=='full_encoding' and (w.get('rule')!=int(form[4:]) or w.get('mode')!=arm or w.get('seed')!=seed):errors.append('Winner metadata mismatch '+name)
   else:errors.append('Missing winner '+name)
   study=dict(family=family,training_objective=objective,formulation=form,trained_arm=arm,method=method,optimizer_seed=seed,study=name,fresh_trial_budget=trials,cached_warm_start_count=12 if family=='full_encoding' else 0,cached_warm_start_scope='Declared protocol count; pinned12-point source per arm/formulation validated, shared across optimizer seeds. Optimizer pickle contents not reloaded.',trial_attempts=len(entries),rows=[])
   for case in selected:
    for evaluated in ['intended','geometric']:
     p=folder/(name+'__'+case['id']+'__'+evaluated+'.json')
     if not p.exists():errors.append('Missing case arm '+str(p));continue
     pin(p);r=read(p);counts['case_arm_rows']+=1;valid=score_valid(r,gate);counts['converged_rows']+=int(valid)
     if not valid:errors.append('Unconverged or malformed case '+str(p))
     if family=='assignment' and r.get('study')!=name:errors.append('Study metadata mismatch '+str(p))
     if family=='full_encoding' and (r.get('trained_arm')!=arm or r.get('optimizer_seed')!=seed or r.get('rule')!=int(form[4:])):errors.append('Ground study metadata mismatch '+str(p))
     params=r.get('pulse',r.get('params'));row_id=r.get('id',r.get('case'));row_arm=r.get('mode',r.get('arm'))
     if row_id!=case['id'] or row_arm!=evaluated or r.get('split')!=split.get(case['seed']):errors.append('Case identity/split mismatch '+str(p))
     if winner is None or canonical(params)!=canonical(winner['params']):errors.append('Pulse not frozen winner '+str(p))
     study['rows'].append(dict(instance_seed=case['seed'],case_id=case['id'],split=r.get('split'),evaluated_arm=evaluated,pulse=params,probabilities={k:r.get('score',{}).get(k) for k in METRICS},rare_absolute_floor={k:r.get('score',{}).get(k,1)<.001 for k in METRICS},relative_accuracy_supported=False,numerical=dict(converged=valid,final_dt=(r.get('history') or [{}])[-1].get('dt'),last_tv=(r.get('history') or [{}])[-1].get('tv_previous')),source_path=str(p),source_sha256=sha(p)))
   studies.append(study)
  coverage[family]=counts
 return dict(coverage=coverage,ready=not errors,errors=errors,source_hashes=snapshots),studies

def aggregate(root=Q,inventory=False):
 audit,studies=inspect(root)
 if inventory:return audit
 if not audit['ready']:raise ValueError('Final aggregation refused: '+ '; '.join(audit['errors'][:12]))
 pairs=[];summaries=[]
 for study in studies:
  header={k:v for k,v in study.items() if k!='rows'}
  for seed in sorted({r['instance_seed'] for r in study['rows']}):
   arms={r['evaluated_arm']:r for r in study['rows'] if r['instance_seed']==seed};a,b=arms['intended'],arms['geometric']
   if canonical(a['pulse'])!=canonical(b['pulse']):raise ValueError('Unmatched paired pulse')
   pairs.append(dict(**header,instance_seed=seed,split=a['split'],pulse=a['pulse'],arms=arms,geometric_minus_intended={k:b['probabilities'][k]-a['probabilities'][k] for k in METRICS}))
  for split in ['development','validation','evaluation']:
   for arm in ['intended','geometric']:
    rs=[r for r in study['rows'] if r['split']==split and r['evaluated_arm']==arm]
    summaries.append(dict(**header,split=split,evaluated_arm=arm,instances=len(rs),metrics={k:dict(mean=statistics.mean(r['probabilities'][k] for r in rs),minimum=min(r['probabilities'][k] for r in rs)) for k in METRICS}))
 fair=[]
 for t in summaries:
  if t['family']!='assignment' or t['method']!='tpe':continue
  random=next(r for r in summaries if r['family']=='assignment' and r['method']=='random' and all(r[k]==t[k] for k in ['formulation','trained_arm','split','evaluated_arm']))
  fair.append(dict(tpe_study=t['study'],random_study=random['study'],optimizer_seed=t['optimizer_seed'],split=t['split'],evaluated_arm=t['evaluated_arm'],trials_per_run=32,mean_difference={k:t['metrics'][k]['mean']-random['metrics'][k]['mean'] for k in METRICS},random_reference_reused=True,independent_comparisons=False))
 return dict(**audit,paired_instances=pairs,study_summaries=summaries,fair_budget_assignment_comparisons=fair,caveats=['Retrospective saved-instance evaluation; correctness/formulation selection used previously inspected instances.','Between-search differences confound objective, pulse family, and formulation/layout menu; descriptive comparisons cannot isolate objective effects.','Assignment: each32-trial TPE run compared separately with one32-trial random run; no pooled-best TPE claim. Random reference is reused, not independent evidence.','Ground:24 fresh trials plus12 shared cached warm starts per study; three optimizer seeds retained; no random comparator exists.','TV<0.001 between successive approximations is empirical absolute stability, not certified error or rare-event relative accuracy.','No best-of-shot probabilities are exported. The single separate rare-tail case does not validate all winner/case/model combinations.','Means/minima are descriptive. Optimizer seeds and interaction arms are not independent problem instances.'])

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Q);p.add_argument('--inventory',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();result=aggregate(a.root,a.inventory);text=json.dumps(result,indent=2,allow_nan=False)
 if a.output:
  if not a.output.resolve().is_relative_to(Path(__file__).resolve().parent):raise ValueError('Output must stay in small_results')
  temp=a.output.with_suffix('.tmp');temp.write_text(text+'\n');temp.replace(a.output)
 else:print(text)
