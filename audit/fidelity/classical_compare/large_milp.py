"""Classical unconstrained binary quadratic comparisons, exact linearization.
No original clustering constraints are added to the search. A solver incumbent
may therefore decode to an invalid or capacity-infeasible clustering.
"""
from pathlib import Path
import argparse,itertools,json,time,hashlib
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
HERE=Path(__file__).resolve().parent

def energy(x,h,J):
    x=np.asarray(x,float)
    return float(h@x+sum(J[i,j]*x[i]*x[j] for i in range(len(x)) for j in range(i+1,len(x))))

def descent(h,J):
    """Deterministic multistart fallback; no optimality certificate."""
    n=len(h);rng=np.random.default_rng(91271);best=None
    for initial in [np.zeros(n,dtype=int),np.ones(n,dtype=int),*(rng.integers(0,2,n) for _ in range(8))]:
        x=initial.copy()
        for _ in range(10000):
            delta=(1-2*x)*(h+J@x);i=int(np.argmin(delta))
            if delta[i]>=-1e-11:break
            x[i]=1-x[i]
        val=energy(x,h,J)
        if best is None or val<best[0]:best=(val,x.copy())
    return best

def solve(h,J,time_limit=10):
    h=np.asarray(h,float);J=np.asarray(J,float);n=len(h)
    if J.shape!=(n,n) or not np.allclose(J,J.T) or not np.allclose(np.diag(J),0):raise ValueError('Expected symmetric full pair coefficients with zero diagonal')
    if not np.isfinite(h).all() or not np.isfinite(J).all():raise ValueError('Nonfinite coefficients')
    ix,iy=np.where(np.triu(J,1)!=0);m=len(ix)
    raw=np.r_[h,J[ix,iy]];scale=max(float(np.max(np.abs(raw))),1e-12);c=raw/scale
    # y <= xi; y <= xj; xi+xj-y <= 1. y stays continuous.
    rr=[];cc=[];vv=[];ub=[]
    for k,(i,j) in enumerate(zip(ix,iy)):
        y=n+k;row=3*k
        rr += [row,row,row+1,row+1,row+2,row+2,row+2]
        cc += [y,int(i),y,int(j),int(i),int(j),y]
        vv += [1,-1,1,-1,1,1,-1];ub += [0,0,1]
    A=coo_matrix((vv,(rr,cc)),shape=(3*m,n+m)).tocsc()
    start=time.perf_counter()
    res=milp(c,integrality=np.r_[np.ones(n),np.zeros(m)],bounds=Bounds(np.zeros(n+m),np.ones(n+m)),
             constraints=LinearConstraint(A,np.full(3*m,-np.inf),ub),options={'time_limit':float(time_limit),'mip_rel_gap':0.,'presolve':True})
    seconds=time.perf_counter()-start
    candidate=None;source=None;raw_candidate=res.x;primal_validation=None
    if raw_candidate is not None and np.isfinite(raw_candidate).all():
        integrality_error=float(np.max(abs(raw_candidate[:n]-np.rint(raw_candidate[:n]))))
        constraint_violation=float(max(0.,np.max(A@raw_candidate-np.asarray(ub)))) if m else 0.
        bounds_violation=float(max(0.,-np.min(raw_candidate),np.max(raw_candidate)-1))
        bits=np.rint(raw_candidate[:n]).astype(int)
        energy_error=abs(energy(bits,h,J)/scale-float(res.fun))
        primal_validation=dict(integrality_error=integrality_error,constraint_violation=constraint_violation,bounds_violation=bounds_violation,normalized_objective_error=energy_error,passed=bool(max(integrality_error,constraint_violation,bounds_violation,energy_error)<=1e-6))
    if raw_candidate is not None and np.isfinite(raw_candidate[:n]).all() and np.max(abs(raw_candidate[:n]-np.rint(raw_candidate[:n])))<1e-5:
        candidate=np.rint(raw_candidate[:n]).astype(int);source='milp_incumbent'
    fallback_val,fallback=descent(h,J)
    if candidate is None or fallback_val<energy(candidate,h,J)-1e-9:
        candidate=fallback;source='deterministic_local_descent'
    val=energy(candidate,h,J);bound=getattr(res,'mip_dual_bound',None)
    bound=float(bound*scale) if bound is not None and np.isfinite(bound) else None
    certified=bool(res.status==0 and primal_validation is not None and primal_validation['passed'] and abs(val-float(res.fun)*scale)<=1e-6*scale)
    if bound is not None and bound>val+1e-6*scale:raise AssertionError('Solver bound exceeds independently evaluated feasible energy')
    return dict(primal_validation=primal_validation,status=int(res.status),message=str(res.message),certified_optimal=bool(certified),seconds=seconds,time_limit_seconds=time_limit,
        objective=val,lower_bound=bound,absolute_gap=max(0.,val-bound) if bound is not None else None,
        relative_gap=max(0.,val-bound)/max(abs(val),1e-12) if bound is not None else None,
        highs_reported_relative_gap=float(res.mip_gap) if getattr(res,'mip_gap',None) is not None and np.isfinite(res.mip_gap) else None,
        normalization_scale=scale,binary_variables=n,continuous_product_variables=m,linear_constraints=3*m,
        incumbent_source=source,bits=''.join(map(str,candidate)),nodes=int(res.mip_node_count) if getattr(res,'mip_node_count',None) is not None else None)

def classify(bits,meta):
    x=np.array(list(bits),int);N=int(meta['N']);K=int(meta['K']);q=np.asarray(meta['q']);Q=float(meta['Q']);c=np.asarray(meta['c']);encoding=meta['encoding']
    if encoding=='reduced':
        z=x[:N*(K-1)].reshape(N,K-1);ok=bool(np.all(z.sum(axis=1)<=1));assignment=np.where(z.sum(axis=1)==0,0,np.argmax(z,axis=1)+1)
    elif encoding=='slack':
        z=x[:N*K].reshape(K,N).T;ok=bool(np.all(z.sum(axis=1)==1));assignment=np.argmax(z,axis=1)
    else:raise ValueError(encoding)
    loads=[float(q[assignment==k].sum()) for k in range(K)] if ok else None
    feasible=bool(ok and max(loads)<=Q+1e-9)
    f=float(sum(c[i,j] for i in range(N) for j in range(i+1,N) if assignment[i]==assignment[j])) if ok else None
    fstar=float(meta['f_star']);optimal=bool(feasible and abs(f-fstar)<=1e-8)
    out=dict(valid_assignment=ok,feasible=feasible,optimal_original_clustering=optimal,assignment=assignment.tolist() if ok else None,loads=loads,
        clustering_objective=f,original_optimum=fstar,clustering_absolute_gap=(f-fstar) if feasible else None,
        clustering_relative_gap=(f-fstar)/abs(fstar) if feasible and fstar else None)
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cases',default=str(HERE/'cases.json'));parser.add_argument('--seconds',type=float,default=10);parser.add_argument('--test',action='store_true');args=parser.parse_args()
    if args.test:return tests()
    manifest=Path(args.cases);data=json.loads(manifest.read_text());cases=data.get('cases',[]) if isinstance(data,dict) else data
    output=HERE/'large_results.json';records=[];superseded=[]
    manifest_hash=hashlib.sha256(manifest.read_bytes()).hexdigest()
    if output.exists():
        previous=json.loads(output.read_text())
        if previous.get('manifest_sha256')!=manifest_hash:raise ValueError('Existing results belong to a different manifest; preserve them before starting another study')
        records=previous['results'];superseded=previous.get('superseded_attempts',[])
        legacy=[r for r in records if 'primal_validation' not in r]
        superseded.extend(legacy);records=[r for r in records if 'primal_validation' in r]
    done={(r['case_id'],r['variant']) for r in records}
    cache={r['coefficient_hash']:r for r in records if r.get('coefficient_hash')}
    cases=sorted(cases,key=lambda c: (0 if c.get('tier',c.get('metadata',{}).get('tier'))=='M' else 1,str(c.get('id',c.get('case_id','')))))
    for case in cases:
        meta={**case,**case.get('metadata',{})}
        if meta.get('tier') not in ['M','L']:continue
        p=Path(case.get('npz_path',case.get('path','')))
        if not p.is_absolute():p=HERE.parents[2]/p
        d=np.load(p);h=d['h_target'];J=d['J_target'];U=d['U']
        variants=[('intended',h,J),('pairs_only',h,U)]
        if 'h_actual' in d.files and d['h_actual'].size:variants.append(('actual_endpoint',d['h_actual'],U))
        for name,hv,jv in variants:
            if (case.get('id',case.get('case_id')),name) in done:continue
            coefficient_hash=hashlib.sha256(np.ascontiguousarray(hv,dtype='<f8').tobytes()+np.ascontiguousarray(jv,dtype='<f8').tobytes()).hexdigest()
            if coefficient_hash in cache:
                original=cache[coefficient_hash];r=dict(original);r.update(reused_from_case=original['case_id'],reused_from_variant=original['variant'],seconds=0.0)
            else:
                r=solve(hv,jv,args.seconds)
            r['coefficient_hash']=coefficient_hash
            r.update(case_id=case.get('id',case.get('case_id')),variant=name,tier=meta['tier'],encoding=meta['encoding'],embedder=meta.get('embedder'),cohort=meta.get('cohort'))
            r['classification']=classify(r['bits'],meta);r['npz_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();records.append(r);cache.setdefault(coefficient_hash,r)
            result=dict(method='Unconstrained QUBO with exact McCormick product linearization; continuous auxiliary products, binary original bits',constant_omitted=True,time_budget_per_solve_seconds=args.seconds,optimality_caveat='Certified means HiGHS reports optimal within numerical tolerances after coefficient normalization; not symbolic exactness. A single incumbent does not characterize all degenerate optima.',manifest_sha256=manifest_hash,superseded_attempts=superseded,results=records)
            tmp=output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False));tmp.replace(output)
            print(json.dumps({k:r[k] for k in ['case_id','variant','status','certified_optimal','objective','lower_bound','seconds']}),flush=True)

def tests():
    import unittest
    class Check(unittest.TestCase):
        def test_signed_random_oracle(self):
            rng=np.random.default_rng(991)
            for n in [1,2,4,6]:
                for _ in range(3):
                    h=rng.integers(-6,7,n).astype(float);J=np.triu(rng.integers(-5,6,(n,n)),1).astype(float);J+=J.T
                    # Exhaustive oracle evaluates monomials explicitly.
                    vals=[sum(float(h[i])*x[i] for i in range(n))+sum(float(J[i,j])*x[i]*x[j] for i in range(n) for j in range(i+1,n)) for x in itertools.product([0,1],repeat=n)]
                    r=solve(h,J,10);self.assertTrue(r['certified_optimal']);self.assertAlmostEqual(r['objective'],min(vals),places=7);self.assertAlmostEqual(r['lower_bound'],min(vals),places=7)
        def test_negative_pair_requires_product(self):
            # Invalid relaxed product would yield -5 instead of true optimum -1.
            r=solve(np.array([2.,2.]),np.array([[0,-5.],[-5.,0]]),10)
            self.assertEqual(r['bits'],'11');self.assertAlmostEqual(r['objective'],-1)
        def test_positive_pair_convention(self):
            r=solve(np.array([-3.,-3.]),np.array([[0,4.],[4.,0]]),10)
            self.assertAlmostEqual(r['objective'],-3)
        def test_invalid_assignment_not_repaired(self):
            m=dict(N=2,K=3,q=[1,1],Q=2,c=[[0,3],[3,0]],f_star=0,encoding='reduced')
            self.assertFalse(classify('1100',m)['valid_assignment'])
        def test_capacity_is_not_solver_constraint(self):
            m=dict(N=2,K=2,q=[2,2],Q=2,c=[[0,3],[3,0]],f_star=0,encoding='reduced')
            r=solve(np.array([-3.,-3.]),np.zeros((2,2)),10);self.assertEqual(r['bits'],'11');self.assertFalse(classify(r['bits'],m)['feasible'])
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Check))
    if not r.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
