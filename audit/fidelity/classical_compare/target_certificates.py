"""Certify primary slack intended minima using exact original references.
Independent square expansion and explicit residual helper-bit construction.
"""
from pathlib import Path
import json,itertools,math
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def main():
    manifest=json.loads((HERE/'cases.json').read_text());rows=[]
    for c in manifest['cases']:
        if c['cohort']!='primary' or c['encoding']!='slack':continue
        folder=ROOT/'audit/scaling/prepared'/c['id'];p=folder/'metadata.json'
        if not p.exists():p=folder/'failure.json'
        meta=json.loads(p.read_text());model=np.load(folder/'model.npz');scaled=np.load(ROOT/c['npz_path'])
        N,K,Q=c['N'],c['K'],c['Q'];q=np.array(c['q']);B=math.ceil(math.log2(Q+1));w=[2**b for b in range(B-1)]+[Q-(2**(B-1)-1)]
        A,W=meta['parameters']['A'],meta['parameters']['W'];n=K*(N+B);h=np.zeros(n);J=np.zeros((n,n));constant=0.
        def square(indices,weights,b,penalty):
            nonlocal constant
            constant+=penalty*b*b
            for i,a in zip(indices,weights):h[i]+=penalty*(a*a-2*b*a)
            for s in range(len(indices)):
                for t in range(s+1,len(indices)):
                    i,j=indices[s],indices[t];v=2*penalty*weights[s]*weights[t];J[i,j]+=v;J[j,i]+=v
        for i in range(N):square([k*N+i for k in range(K)],[1]*K,1,A)
        for k in range(K):
            square(list(range(k*N,(k+1)*N))+list(range(K*N+k*B,K*N+(k+1)*B)),list(q)+w,Q,W)
            for i in range(N):
                for j in range(i+1,N):J[k*N+i,k*N+j]+=c['c'][i][j];J[k*N+j,k*N+i]+=c['c'][i][j]
        assert np.allclose(h,model['h'],rtol=1e-12,atol=1e-8)
        assert np.allclose(J,model['J'],rtol=1e-12,atol=1e-8)
        assert abs(constant-float(model['const']))<1e-7
        z=np.zeros(n);partition=c['reference_partition'];assert sorted(itertools.chain.from_iterable(partition))==list(range(N))
        loads=[]
        for k in range(K):
            group=partition[k] if k<len(partition) else [];load=sum(q[i] for i in group);loads.append(int(load));assert load<=Q
            for i in group:z[k*N+i]=1
            helper=next(v for v in itertools.product([0,1],repeat=B) if sum(a*b for a,b in zip(w,v))==Q-load)
            z[K*N+k*B:K*N+(k+1)*B]=helper
        original=sum(c['c'][i][j] for group in partition for i,j in itertools.combinations(group,2));assert abs(original-c['f_star'])<1e-8
        assert c['reference_status']=='proven_exact_subset_dynamic_programming'
        assert min(A,W)>c['f_star'] and np.all(q==q.astype(int)) and np.all(np.array(c['c'])>=0) and all(int(v)==v and v>0 for v in w)
        alpha=c['alpha'];assert alpha>0
        assert np.allclose(scaled['h_target'],alpha*model['h'],rtol=1e-12,atol=1e-10)
        assert np.allclose(scaled['J_target'],alpha*model['J'],rtol=1e-12,atol=1e-10)
        energy=float(scaled['h_target']@z+.5*z@scaled['J_target']@z);expected=alpha*(c['f_star']-float(model['const']))
        assert abs(energy-expected)<1e-8
        rows.append(dict(id=c['id'],tier=c['tier'],instance_seed=c['instance_seed'],atoms=n,all_intended_groundstates_feasible=True,all_intended_groundstates_original_optimal=True,
            minimum_constraint_violation_penalty=min(A,W),original_optimum=c['f_star'],constraint_violation_margin=min(A,W)-c['f_star'],scaled_constraint_violation_margin=alpha*(min(A,W)-c['f_star']),
            certified_intended_energy=expected,explicit_bitstring=''.join(str(int(v)) for v in z),loads=loads,energy_check_error=abs(energy-expected)))
    out=dict(proof='Nonnegative distance objective; every violated integer assignment/capacity square costs at least min(A,W)>f_star. Exact reference partition admits represented nonnegative residual slack and attains f_star. Positive alpha preserves minimizers. Independently reconstructed polynomial matches saved model.',cases=len(rows),independent_instances=len({(r['tier'],r['instance_seed']) for r in rows}),rows=rows)
    (HERE/'target_certificates.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))

if __name__=='__main__':main()
