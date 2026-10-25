import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import subprocess,sys,json,time,hashlib
H=Path(__file__).resolve().parent
runs=[('M_2002_reduced_original_intended',10),('M_2002_reduced_original_geometric',10),('M_2002_reduced_original_intended',5)]
summary={'worker_sha256':hashlib.sha256((H/'worker.py').read_bytes()).hexdigest(),'per_run_wall_limit_seconds':1200,'cpu_threads':1,'runs':[],'complete':False}
for name,dt in runs:
 output=H/(name+'_dt'+str(dt));output.mkdir(exist_ok=True);start=time.monotonic()
 with (output/'stdout.log').open('w') as f:
  try:
   p=subprocess.run([sys.executable,str(H/'worker.py'),name,str(dt)],stdout=f,stderr=subprocess.STDOUT,timeout=1200);outcome='process_completed' if p.returncode==0 else 'process_failed'
  except subprocess.TimeoutExpired:outcome='wall_timeout'
 row={'name':name,'dt':dt,'process_outcome':outcome,'elapsed_seconds':time.monotonic()-start}
 if (output/'status.json').exists():
  status=json.loads((output/'status.json').read_text())
  if outcome=='wall_timeout':status.update(status='timeout',seconds=row['elapsed_seconds']);(output/'status.json').write_text(json.dumps(status,indent=2))
  row['result']=status
 summary['runs'].append(row);(H/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(row),flush=True)
 if outcome=='wall_timeout':break
summary['complete']=len(summary['runs'])==3;summary['all_passed']=summary['complete'] and all(r['result'].get('status')=='completed' for r in summary['runs']);(H/'summary.json').write_text(json.dumps(summary,indent=2))
