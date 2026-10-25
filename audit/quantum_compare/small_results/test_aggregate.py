import json,tempfile,unittest
from pathlib import Path
from aggregate import aggregate,sha,METRICS,SEEDS

def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
class AggregationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.q=Path(self.tmp.name)/'audit/quantum_compare';seeds=list(range(10));params={'duration':4.};score={**{k:.02 for k in METRICS},'normalization_error':-1e-14};fine=dict(converged=True,score=score,history=[dict(dt=.0025,tv_previous=.0001,score=score)])
  a=self.q/'tuning_small';g=self.q/'formulation_search/full_ground_tuning';layout=self.q/'formulation_search/transfer_layouts/manifest.json';coarse=self.q/'formulation_search/quantum_screen/coarse_progress.json';put(coarse,{'returned':72,'rows':[{'rule':r,'mode':a,'pulse_index':i} for r in [0,1,24] for a in ['intended','geometric'] for i in range(12)]})
  artifact=self.q/'fixture.bin';artifact.parent.mkdir(parents=True,exist_ok=True);artifact.write_bytes(b'frozen target and geometry');relative=str(artifact.relative_to(self.q.parents[1]));dh=sha(artifact)
  put(layout,{'rows':[{'id':f'S_slack_{s}_rule{r}','target':{'family':'S_slack','instance_seed':s,'rule_index':r,'npz_path':relative,'npz_hash':dh},'selected_geometry':{'geometry_path':relative,'geometry_hash':dh}} for s in seeds for r in [0,1,24]]})
  am=self.q/'small_geometry_manifest.json';put(am,{'targets':[{'id':f'S_{s}_slack_{v}','geometry_path':relative,'target_path':relative} for s in seeds for v in ['original','alternative']]})
  put(a/'protocol.json',dict(manifest_hash=sha(am),trial_budget=32,tpe_seeds=list(SEEDS),random_seeds=[11],source_hashes={},inputs=[{'id':f'S_{s}_slack_{v}','geometry_hash':dh,'target_hash':dh} for s in seeds for v in ['original','alternative']],development=seeds[:3],validation=seeds[3:5],evaluation=seeds[5:],convergence_TV_gate=.001))
  put(g/'protocol.json',dict(new_adaptive_trials_per_study=24,warm_starts=12,seeds=list(SEEDS),formulation_rules=[0,1,24],sources={},layout_manifest_hash=sha(layout),warm_start_source_hash=sha(coarse),development_instances=seeds[:3],fine_gate_TV=.001))
  put(a/'complete.json',dict(complete=True,studies=16,trials_per_study=32,manifest_hash=sha(am)));put(g/'execution_complete.json',dict(complete=True,studies=18,new_trials=432))
  for family,folder,forms in [('assignment',a,['original','alternative']),('full_encoding',g,['rule0','rule1','rule24'])]:
   for form in forms:
    for trained in ['intended','geometric']:
     for method,ss in ([('tpe',SEEDS),('random',[11])] if family=='assignment' else [('tpe',SEEDS)]):
      for optseed in ss:
       name=f'{form}_{trained}_{method}_{optseed}' if family=='assignment' else f'{form}_{trained}_{optseed}';n=32 if family=='assignment' else 24;entries=[dict(trial=i if family=='assignment' else i+12,state='COMPLETE',attributes={'cached_warm_start':False}) for i in range(n)];(folder/(name+'.jsonl')).write_text('\n'.join(json.dumps(e) for e in entries))
       mean='mean_optimal' if family=='assignment' else 'mean_ground_probability';finalists=[dict(trial=i,params=params,all_converged=True,rows=[dict(**fine,**({'id':f'S_{ds}_slack_{form}'} if family=='assignment' else {'case':f'S_slack_{ds}_{form}'})) for ds in seeds[:3]],**{mean:.02}) for i in range(3)];w=dict(winner=finalists[0],finalists=finalists)
       w.update(dict(study=name,variant=form,trained_mode=trained,method=method,seed=optseed) if family=='assignment' else dict(rule=int(form[4:]),mode=trained,seed=optseed));put(folder/(name+'_winner.json'),w)
       for seed in seeds:
        case=f'S_{seed}_slack_{form}' if family=='assignment' else f'S_slack_{seed}_{form}'
        for arm in ['intended','geometric']:
         r=dict(**fine,split='development' if seed<3 else 'validation' if seed<5 else 'evaluation',p_any_optimal_2000_independent_shots=.99)
         r.update(dict(id=case,mode=arm,study=name,pulse=params) if family=='assignment' else dict(case=case,arm=arm,trained_arm=trained,optimizer_seed=optseed,rule=int(form[4:]),params=params));put(folder/(name+'__'+case+'__'+arm+'.json'),r)
 def test_complete_preserves_objectives_seeds_pairs_and_fair_comparisons(self):
  r=aggregate(self.q);self.assertEqual(len(r['paired_instances']),340);self.assertEqual(len(r['fair_budget_assignment_comparisons']),72);self.assertEqual({p['optimizer_seed'] for p in r['paired_instances'] if p['method']=='tpe'},set(SEEDS));self.assertEqual({p['training_objective'] for p in r['paired_instances']},{'optimal','optimal_full_encoding'});self.assertTrue(all(len(p['arms'])==2 for p in r['paired_instances']));self.assertNotIn('p_any_',json.dumps(r));self.assertTrue(all(x['random_reference_reused'] for x in r['fair_budget_assignment_comparisons']))
 def test_rare_tail_flag_and_no_derived_shot_claim(self):
  p=next((self.q/'formulation_search/full_ground_tuning').glob('*__*__geometric.json'));r=json.loads(p.read_text());r['score']['optimal_full_encoding']=1e-12;r['history'][-1]['score']['optimal_full_encoding']=1e-12;put(p,r)
  out=aggregate(self.q);rows=[a for pair in out['paired_instances'] for a in pair['arms'].values() if a['source_path']==str(p)];self.assertEqual(len(rows),1);self.assertTrue(rows[0]['rare_absolute_floor']['optimal_full_encoding']);self.assertFalse(rows[0]['relative_accuracy_supported']);self.assertNotIn('p_any_',json.dumps(out));self.assertTrue(all(p['cached_warm_start_count']==12 for p in out['paired_instances'] if p['family']=='full_encoding'))
 def test_missing_marker_refuses_final_inventory_has_no_probabilities(self):
  (self.q/'tuning_small/complete.json').unlink();r=aggregate(self.q,True);self.assertFalse(r['ready']);self.assertNotIn('paired_instances',r)
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_missing_arm_refuses_final(self):
  next((self.q/'tuning_small').glob('*__*__geometric.json')).unlink()
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_nonconverged_row_refuses_final(self):
  p=next((self.q/'tuning_small').glob('*__*__geometric.json'));r=json.loads(p.read_text());r['converged']=False;put(p,r)
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_wrong_winner_pulse_refuses_final(self):
  p=next((self.q/'tuning_small').glob('*__*__geometric.json'));r=json.loads(p.read_text());r['pulse']={'duration':9.};put(p,r)
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_insufficient_budget_refuses_final(self):
  p=next((self.q/'tuning_small').glob('*.jsonl'));p.write_text('\n'.join(p.read_text().splitlines()[:-1]))
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_actual_target_geometry_drift_refuses_final(self):
  (self.q/'fixture.bin').write_bytes(b'changed data')
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_duplicate_development_case_refuses_final(self):
  p=next((self.q/'tuning_small').glob('*_winner.json'));r=json.loads(p.read_text());r['finalists'][0]['rows'][1]=r['finalists'][0]['rows'][0];r['winner']=r['finalists'][0];put(p,r)
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_malformed_probability_and_tv_refuse_final(self):
  p=next((self.q/'tuning_small').glob('*__*__geometric.json'));original=json.loads(p.read_text())
  for mutation in ['negative_tv','bad_norm','hierarchy']:
   r=json.loads(json.dumps(original))
   if mutation=='negative_tv':r['history'][-1]['tv_previous']=-.2
   elif mutation=='bad_norm':r['score']['normalization_error']=.5
   else:r['score']['optimal']=.8;r['history'][-1]['score']['optimal']=.8
   put(p,r)
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):aggregate(self.q)
 def test_wrong_fresh_trial_indices_refuse_final(self):
  p=next((self.q/'formulation_search/full_ground_tuning').glob('*.jsonl'));r=[json.loads(l) for l in p.read_text().splitlines()]
  for x in r:x['trial']-=12
  p.write_text('\n'.join(json.dumps(x) for x in r))
  with self.assertRaises(ValueError):aggregate(self.q)
 def test_source_drift_refuses_final(self):
  p=self.q/'formulation_search/quantum_screen/coarse_progress.json';p.write_text(p.read_text()+' ')
  with self.assertRaises(ValueError):aggregate(self.q)
if __name__=='__main__':unittest.main(verbosity=2)
