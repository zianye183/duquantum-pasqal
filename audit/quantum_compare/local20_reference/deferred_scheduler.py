import os,time,json,hashlib,subprocess,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent
stamp=lambda:datetime.now(ZoneInfo('America/New_York')).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release=dict(status='waiting_for_original_worker_exit',authorized_by='parent explicit message: one unchanged-input rerun after PID93809 absent,3600s cap oneCPU',released_at=stamp(),scheduler_pid=os.getpid(),wait_for_pid=93809,plan_sha256=sha(H/'deferred_retry3600_plan.json'),scheduler_sha256=sha(Path(__file__)),analysis_source_hashes={n:sha(H/n) for n in ['global_cloud_check_retry.py','geometric_compare_retry.py']})
def save(): (H/'deferred_release.json').write_text(json.dumps(release,indent=2))
save();print(json.dumps(release),flush=True)
while True:
 try:os.kill(93809,0)
 except ProcessLookupError:break
 time.sleep(30)
release.update(status='executing_authorized_single_retry',started_at=stamp());save()
with (H/'deferred_retry_stdout.log').open('w') as f:
 r=subprocess.run([sys.executable,str(H/'deferred_retry3600.py')],stdout=f,stderr=subprocess.STDOUT)
release.update(process_returncode=r.returncode,finished_at=stamp())
summary=H/'geometric_retry3600_summary.json'
if r.returncode==0 and summary.exists() and json.loads(summary.read_text()).get('all_passed'):
 release['status']='quantum_complete_analysis_running';save()
 for script in ['geometric_compare_retry.py','global_cloud_check_retry.py']:
  with (H/(script+'.log')).open('w') as f:r=subprocess.run([sys.executable,str(H/script)],stdout=f,stderr=subprocess.STDOUT)
  if r.returncode:release.update(status='analysis_failed',failed_script=script);save();raise SystemExit(r.returncode)
 release['status']='complete'
else:release['status']='retry_not_successful_no_further_quantum_run'
save();print(json.dumps(release),flush=True)
