"""Bound energies of decoded-feasible primary medium slack assignments.
Helper bits are unconstrained. No new cloud jobs; five seconds per MILP.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def solve(h,J,c):
    n=len(h);ix,iy=np.where(np.triu(J,1)!=0);m=len(ix);scale=max(np.max(abs(h)),np.max(abs(J)),1e-12)
    objective=np.r_[h,J[ix,iy]]/scale;ri=[];ci=[];v=[];lb=[];ub=[]
    def add(indices,values,lo,hi):
        row=len(lb);ri.extend([row]*len(indices));ci.extend(indices);v.extend(values);lb.append(lo);ub.append(hi)
    for k,(i,j) in enumerate(zip(ix,iy)):
        y=n+k;add([y,i],[1,-1],-np.inf,0);add([y,j],[1,-1],-np.inf,0);add([i,j,y],[1,1,-1],-np.inf,1)
    N,K=c['N'],c['K']
    for i in range(N):add([k*N+i for k in range(K)],[1]*K,1,1)
    for k in range(K):add([k*N+i for i in range(N)],c['q'],-np.inf,c['Q'])
    matrix=coo_matrix((v,(ri,ci)),shape=(len(lb),n+m)).tocsc();start=time.monotonic()
    r=milp(objective,integrality=np.r_[np.ones(n),np.zeros(m)],bounds=Bounds(np.zeros(n+m),np.ones(n+m)),constraints=LinearConstraint(matrix,lb,ub),options={'time_limit':5.,'mip_rel_gap':0.})
    bound=getattr(r,'mip_dual_bound',None);bound=float(bound*scale) if bound is not None and np.isfinite(bound) else None
    incumbent=None;bits=None
    if r.x is not None and np.max(abs(r.x[:n]-np.rint(r.x[:n])))<1e-6:
        z=np.rint(r.x[:n]);X=z[:N*K].reshape(K,N)
        assert np.all(X.sum(0)==1) and np.all(X@np.array(c['q'])<=c['Q'])
        incumbent=float(h@z+.5*z@J@z);bits=''.join(str(int(t)) for t in z)
    return dict(status=int(r.status),message=str(r.message),seconds=time.monotonic()-start,lower_bound=bound,feasible_incumbent_energy=incumbent,feasible_incumbent_bits=bits,normalization_scale=float(scale),time_limit_seconds=5.)

def main():
    mp=HERE/'cases.json';manifest=json.loads(mp.read_text());digest=hashlib.sha256(mp.read_bytes()).hexdigest();p=HERE/'physical_feasible_bounds.json'
    old=json.loads(p.read_text()) if p.exists() else None
    if old:assert old['manifest_sha256']==digest
    rows=old['rows'] if old else [];lookup={(r['id'],r['variant']):r for r in rows}
    for c in manifest['cases']:
        if c['tier']!='M' or c['encoding']!='slack' or c['cohort']!='primary':continue
        model=np.load(ROOT/c['npz_path'])
        for variant in ['pairs_only','actual_endpoint']:
            if variant=='actual_endpoint' and not len(model['h_actual']):continue
            if (c['id'],variant) in lookup:continue
            h=model['h_actual'] if variant=='actual_endpoint' else model['h_target'];r=solve(h,model['U'],c);r.update(id=c['id'],variant=variant,embedder=c['embedder'],instance_seed=c['instance_seed']);rows.append(r)
            output=dict(manifest_sha256=digest,method='McCormick pair products; original assignment equality and capacity inequality only; helper bits remain free',rows=rows)
            p.write_text(json.dumps(output,indent=2));print(c['id'],variant,r['status'],flush=True)
    unconstrained=json.loads((HERE/'large_results.json').read_text())['results']
    byid={c['id']:c for c in manifest['cases']}
    for r in rows:
        matches=[u for u in unconstrained if u['case_id']==r['id'] and u['variant']==r['variant']]
        r['proves_no_feasible_groundstate']=False
        if matches and r['lower_bound'] is not None:
            u=min(matches,key=lambda u:u['objective']);tol=1e-5*r['normalization_scale']
            model=np.load(ROOT/byid[r['id']]['npz_path']);bits=np.array([int(b) for b in u['bits']]);assert set(u['bits'])<={'0','1'} and len(bits)==len(model['h_target'])
            h=model['h_actual'] if r['variant']=='actual_endpoint' else model['h_target']
            witness=float(h@bits+.5*bits@model['U']@bits)
            assert abs(witness-u['objective'])<1e-8
            r.update(unconstrained_incumbent_energy=witness,separation=r['lower_bound']-witness,comparison_tolerance=tol,proves_no_feasible_groundstate=bool(r['lower_bound']>witness+tol))
    output=dict(manifest_sha256=digest,method='McCormick pair products; original assignment equality and capacity inequality only; helper bits remain free',proof='Feasible-set lower bound strictly exceeds energy of an unconstrained binary witness, with conservative numerical margin. Conditional on floating-point solver bounds, not formal exact arithmetic.',solves=len(rows),solver_seconds=sum(r['seconds'] for r in rows),proved_no_feasible_groundstates=sum(r['proves_no_feasible_groundstate'] for r in rows),rows=rows)
    p.write_text(json.dumps(output,indent=2));print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))

if __name__=='__main__':main()
