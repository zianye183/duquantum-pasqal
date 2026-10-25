import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import sys,json,time,hashlib,itertools
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'snapshot'))
import dynamics as d, embedding as e, track_a as t

def stamp():return datetime.now(ZoneInfo('America/New_York')).isoformat()
def save(name,obj):
 p=HERE/name;p.write_text(json.dumps(obj,indent=2,allow_nan=False))
def full(I,A,mu):
 N,K,Q,q,c=[I[k] for k in ['N','K','Q','q','c']];n=N*K
 h=np.zeros(n);J=np.zeros((n,n));const=A*N+mu*K*Q*Q
 for k in range(K):
  for i in range(N):h[k*N+i]=-A+mu*(q[i]**2-2*Q*q[i])
  for i,j in itertools.combinations(range(N),2):J[k*N+i,k*N+j]=c[i,j]+2*mu*q[i]*q[j]
 for i in range(N):
  for k,l in itertools.combinations(range(K),2):J[k*N+i,l*N+i]=2*A
 return h,J+J.T,const

def inspect(I,enc,h,J,const,A,W):
 N,K,Q,q,c=[I[k] for k in ['N','K','Q','q','c']];n=len(h)
 z=((np.arange(1<<n)[:,None]>>np.arange(n))&1).astype(float)
 if enc=='reduced_balance':
  v=z.reshape(-1,N,K-1);X=np.concatenate([1-v.sum(2,keepdims=True),v],axis=2).transpose(0,2,1)
  assign=(v.sum(2)<=1).all(1);pen=A*sum(v[:,:,a]*v[:,:,b] for a,b in itertools.combinations(range(K-1),2)) if K>2 else np.zeros((len(z),N));assignpen=np.sum(pen,axis=1)
 else:
  X=z[:,:N*K].reshape(-1,K,N);assign=(X.sum(1)==1).all(1);assignpen=A*((X.sum(1)-1)**2).sum(1)
 loads=X@q;cost=sum(c[i,j]*(X[:,:,i]*X[:,:,j]).sum(1) for i,j in itertools.combinations(range(N),2))
 feasible=assign&(loads<=Q).all(1);optimal=feasible&np.isclose(cost,I['f_star'],rtol=0,atol=1e-8)
 if enc=='slack':
  spare=z[:,N*K:].reshape(-1,K,len(t.slack_weights(Q)))@t.slack_weights(Q)
  residual=loads+spare-Q;complete=optimal&(residual==0).all(1)
 else:residual=loads-Q;complete=optimal
 direct=cost+assignpen+W*(residual**2).sum(1)
 model=d.DiagonalProblem(h,J);err=float(abs(direct-(model.linear+model.pairs+const)).max());assert err<1e-7,(enc,err)
 return {'assignment_valid':assign,'feasible':feasible,'optimal':optimal,'complete_optimal':complete},err

def scores(p,m):return {k:float(p[v].sum()) for k,v in m.items()}

def refined(model,pulse):
 prev=None;trail=[]
 for dt in [.01,.005,.0025,.00125,.000625,.0003125]:
  r=d.evolve(model,pulse,dt);p=r['probabilities'];assert abs(p.sum()-1)<1e-8
  tv=None if prev is None else float(abs(p-prev).sum()/2)
  trail.append({'dt':dt,'tv_previous':tv,'seconds':r['seconds']})
  if tv is not None and tv<1e-4:return p,trail,True
  prev=p
 return p,trail,False

start=time.monotonic();rows=[];manifest={'started_at':stamp(),'status':'running','cloud_jobs':0,'protocol_sha256':hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest(),'source_hashes':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*sorted((HERE/'snapshot').glob('*.*'))]}}
save('manifest.json',manifest)
data=json.loads((HERE/'snapshot/instances.json').read_text())['instances']
for seed in [2002,2006,2012]:
 raw=next(x for x in data if x['tier']=='S' and x['seed']==seed);I={**raw,'q':np.array(raw['q']),'c':np.array(raw['c'])}
 N,K,Q=I['N'],I['K'],I['Q'];assigns=np.array(list(itertools.product(range(K),repeat=N)))
 loads=np.stack([(assigns==k)@I['q'] for k in range(K)],axis=1);feas=(loads<=Q).all(1)
 costs=np.array([sum(I['c'][i,j] for i,j in itertools.combinations(range(N),2) if a[i]==a[j]) for a in assigns])
 I['f_star']=float(costs[feas].min());certificate=assigns[np.flatnonzero(feas)[0]];fc=float(t.cluster_cost(certificate,I['c']));cl=loads[np.flatnonzero(feas)[0]];mu=t.mu_equal_weight(I)
 for enc in ['slack','full_balance','reduced_balance']:
  if enc=='slack':A=W=float(np.ceil(fc+1));h,J,const=t.build_slack_qubo(I,A,W)
  elif enc=='full_balance':W=mu;A=float(np.ceil(fc+mu*((cl-Q)**2).sum()+1));h,J,const=full(I,A,W)
  else:W=mu;A=t.m_bound(I,mu);h,J,const=t.build_onehot_qubo(I,A,W)
  masks,err=inspect(I,enc,h,J,const,A,W);key=f'{seed}_{enc}'
  emb=e.embed(h,J,'blade',0,maxiter=300);save(key+'_layout.json',emb)
  row={'seed':seed,'encoding':enc,'atoms':len(h),'assignment_weight':A,'capacity_or_balance_weight':W,'algebra_max_error':err,'f_star':I['f_star'],'geometry_valid':emb['physical_valid'],'pair_error':emb['eps_J'],'alpha':emb['alpha'],'arms':{}}
  if not emb['physical_valid']:
   row['status']='invalid_geometry';rows.append(row);save('progress.json',rows);continue
  U=np.array(emb['realized_U']);alpha=emb['alpha'];pulse=d.Pulse()
  for arm,pairs in [('exact',alpha*J),('geometric',U)]:
   model=d.DiagonalProblem(alpha*h,pairs);p,trail,ok=refined(model,pulse);endpoint=model.linear+model.pairs;ground=np.isclose(endpoint,endpoint.min(),rtol=0,atol=1e-8)
   res={'probability':scores(p,masks),'numerical_gate_passed':ok,'refinement':trail,'endpoint_all_minima_feasible':bool(masks['feasible'][ground].all()),'endpoint_all_minima_original_optimal':bool(masks['optimal'][ground].all()),'ground_count':int(ground.sum())}
   if seed==2002 and enc=='full_balance':
    labels=np.arange(1<<len(h));flips=np.array([labels^(1<<i) for i in range(len(h))]);init=np.zeros(len(labels),complex);init[0]=1
    def rhs(tm,psi):
     sc=tm/pulse.duration
     return -1j*(model.diagonal(sc,pulse)*psi+model.amplitude(sc,pulse)/2*psi[flips].sum(0))
    tt=time.monotonic();sol=solve_ivp(rhs,[0,pulse.duration],init,method='DOP853',rtol=1e-10,atol=1e-12,t_eval=[pulse.duration]);assert sol.success
    ref=abs(sol.y[:,-1])**2;tv=float(abs(ref-p).sum()/2);res['independent_DOP853']={'tv':tv,'passed':tv<1e-4,'norm':float(ref.sum()),'seconds':time.monotonic()-tt};assert tv<1e-4
   row['arms'][arm]=res
   np.savez_compressed(HERE/(key+'_'+arm+'.npz'),probabilities=p,h=alpha*h,J=pairs,**masks)
   print(seed,enc,arm,res['probability'], 'gate',ok,flush=True)
  row['status']='complete' if all(r['numerical_gate_passed'] for r in row['arms'].values()) else 'needs_refinement'
  rows.append(row);save('progress.json',rows)
summary={}
for enc in ['slack','full_balance','reduced_balance']:
 rr=[r for r in rows if r['encoding']==enc];summary[enc]={'cases':len(rr),'completed':sum(r['status']=='complete' for r in rr)}
 if summary[enc]['completed']==3:
  summary[enc]['means']={arm:{metric:float(np.mean([r['arms'][arm]['probability'][metric] for r in rr])) for metric in ['feasible','optimal','complete_optimal']} for arm in ['exact','geometric']}
manifest.update(status='complete' if all(r['status']=='complete' for r in rows) else 'incomplete',finished_at=stamp(),elapsed_seconds=time.monotonic()-start,summary=summary)
save('manifest.json',manifest);save('results.json',{'manifest':manifest,'rows':rows});print(json.dumps(summary),flush=True)
