"""Offline submission replay. Never connects to cloud or launches paid jobs."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,csv,hashlib,importlib.util,json,subprocess,sys,tempfile,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def read(p):return json.loads(p.read_text())
def run():
 ap=argparse.ArgumentParser();ap.add_argument('--simulate',action='store_true',help='Rerun the 18 small matched dynamics in a scratch copy');ap.add_argument('--cplex',action='store_true',help='Recheck ten small exact references; requires CPLEX');args=ap.parse_args();start=time.monotonic();out={}
 checks=read(ROOT/'submission/SHA256SUMS.json')
 for name,h in checks.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,('file changed',name)
 out['pinned_files_verified']=len(checks)
 scorer=load('raw_verifier','audit/scaling/verify_observed_counts.py')
 instances=read(ROOT/'audit/scaling/references/instances.json')['instances'];by={(i['tier'],i['seed']):i for i in instances}
 refs=load('references','audit/scaling/references.py')
 for i in instances:
  raw=refs.make_candidate(i['tier'],i['seed']);assert raw['demands']==i['q'];assert raw['coordinates']==i['xy']
  a=i['certificate_feasible_only'];assert len(a)==i['N'] and all(0<=x<i['K'] for x in a)
  assert max(sum(i['q'][j] for j,x in enumerate(a) if x==k) for k in range(i['K']))<=i['Q']
 out['instances_and_certificates']=len(instances)
 manifest=read(ROOT/'audit/scaling/replay_manifest.json');rows={r['id']:r for r in csv.DictReader((ROOT/'submission/results_track_a.csv').open())};unique=set()
 for r in manifest:
  p=ROOT/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['counts_sha256'];parts=r['id'].split('_');I=by[parts[0],int(parts[1])]
  result=scorer.evaluate(read(p),r['result_atom_order'],I,parts[2])
  for k,v in r['independent_result'].items():
   if isinstance(v,(float,int)):assert abs(result[k]-v)<1e-8,(r['id'],k)
   else:assert result[k]==v,(r['id'],k)
  if r['cohort']=='primary':
   for k in ['feasibility_rate','optimal_clustering_rate','optimal_cvrp_rate','model_gap_pct','cvrp_gap_pct']:
    saved=scorer.number(rows[r['id']].get(k));value=result[k];assert (saved is None)==(value is None),(r['id'],k,saved,value)
    if value is not None:assert abs(saved-value)<1e-8
  unique.add((r['counts_sha256'],tuple(r['result_atom_order']),r['id']))
 out['raw_count_conditions_rescored']=len(manifest);out['primary_conditions']=len(rows);out['primary_completed']=sum(r['status']=='completed' for r in rows.values())
 # Aggregate the frozen pulse trials, validating source hashes and winner identity.
 agg=load('pulse_aggregate','audit/quantum_compare/small_results/aggregate.py');pulse=agg.aggregate(ROOT/'audit/quantum_compare');out['pulse_coverage']=pulse['coverage']
 # Cloud counts are replayed without contacting the cloud.
 sys.path.insert(0,str(ROOT/'audit/quantum_compare'));cloud=load('cloud_score','audit/quantum_compare/score_cloud.py')
 for label in ['ramp14','ramp_remaining']:
  result=cloud.analyze(ROOT/f'audit/quantum_compare/{label}_prepared',ROOT/f'audit/quantum_compare/{label}_results');saved=read(ROOT/f'audit/quantum_compare/{label}_score.json')
  assert result['completed']==saved['completed']
  expected={r['id']:r for r in saved['rows']}
  for row in result['rows']:
   if row['status']=='completed':assert row['metrics']==expected[row['id']]['metrics']
  out[label+'_completed']=result['completed']
 with tempfile.TemporaryDirectory(prefix='pasqal-replay-') as tmp:
  tmp=Path(tmp).resolve();matched=tmp/'matched';shutil.copytree(ROOT/'audit/encoding_matched_controls',matched,ignore=shutil.ignore_patterns('__pycache__'))
  subprocess.run([sys.executable,str(matched/'summarize.py')],check=True,stdout=subprocess.DEVNULL);out['matched_distributions_rescored']=18
  if args.simulate:
   subprocess.run([sys.executable,str(matched/'run.py')],check=True,stdout=subprocess.DEVNULL)
   fresh=read(matched/'results.json');old=read(ROOT/'audit/encoding_matched_controls/results.json');assert fresh['manifest']['status']=='complete'
   delta=max(abs(a['arms'][arm]['probability'][metric]-b['arms'][arm]['probability'][metric]) for a,b in zip(fresh['rows'],old['rows']) for arm in ['exact','geometric'] for metric in ['feasible','optimal'])
   assert delta<1e-4,delta;out['fresh_simulation_max_probability_difference']=delta
  if args.cplex:
   dest=tmp/'submission/cplex';shutil.copytree(ROOT/'submission/cplex',dest);data=tmp/'audit/scaling/references';data.mkdir(parents=True);shutil.copy2(ROOT/'audit/scaling/references/instances.json',data/'instances.json')
   subprocess.run([sys.executable,str(dest/'verify_references.py')],check=True);out['cplex_reference_solves']=20
 out['status']='passed';out['elapsed_seconds']=time.monotonic()-start;out['new_cloud_jobs']=0
 dest=ROOT/'reproduction_output';dest.mkdir(exist_ok=True);(dest/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':run()
