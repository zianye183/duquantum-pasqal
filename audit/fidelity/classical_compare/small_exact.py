"""Exhaustive <=20-bit intended/interaction-distorted/actual-endpoint solves.
No production decoding or energy functions are imported. Energies omit constants.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse,hashlib,itertools,json,math,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
TOL=1e-8

def states(n):
    labels=np.arange(1<<n,dtype=np.uint32);z=np.empty((1<<n,n),dtype=np.uint8)
    for col in range(n):z[:,col]=(labels>>col)&1
    return z

def energy(z,h,J):
    out=np.zeros(len(z),dtype=float)
    for i in range(len(h)):out+=h[i]*z[:,i]
    for i,j in itertools.combinations(range(len(h)),2):out+=J[i,j]*z[:,i]*z[:,j]
    return out

def decode(z,I,encoding):
    N,K,Q=I['N'],I['K'],I['Q'];q=np.asarray(I['q']);c=np.asarray(I['c'])
    if encoding=='slack':
        X=z[:,:N*K].reshape(-1,K,N).transpose(0,2,1)
        assignment_valid=(X.sum(axis=2)==1).all(axis=1)
        B=z.shape[1]//K-N
        weights=np.array([2**b for b in range(B-1)]+[Q-(2**(B-1)-1)])
        slack=z[:,N*K:].reshape(-1,K,B)@weights
    else:
        partial=z.reshape(-1,N,K-1).astype(np.int8)
        assignment_valid=(partial.sum(axis=2)<=1).all(axis=1)
        X=np.concatenate([(1-partial.sum(axis=2))[:,:,None],partial],axis=2);slack=None
    loads=np.einsum('i,bik->bk',q,X)
    capacity_feasible=(loads<=Q).all(axis=1)&(loads>=0).all(axis=1)
    feasible=assignment_valid&capacity_feasible
    cost=sum(c[i,j]*(X[:,i,:]*X[:,j,:]).sum(axis=1) for i,j in itertools.combinations(range(N),2))
    optimal=feasible&np.isclose(cost,float(I['f_star']),rtol=0,atol=TOL)
    helper_exact=((loads+slack==Q).all(axis=1)) if slack is not None else None
    return dict(assignment_valid=assignment_valid,capacity_feasible=capacity_feasible,feasible=feasible,optimal=optimal,helper_exact=helper_exact,cost=cost,f_star=float(I['f_star']))

def summarize(E,target_E,d,z):
    e0=float(E.min());gs=abs(E-e0)<=TOL;outside=~gs
    out=dict(ground_energy=e0,ground_state_count=int(gs.sum()),next_distinct_energy_gap=float(E[outside].min()-e0) if outside.any() else None,minimizer_bits=[''.join(map(str,row.astype(int))) for row in z[gs]],minimizer_state_integers=np.flatnonzero(gs).tolist())
    for label in ['assignment_valid','capacity_feasible','feasible','optimal','helper_exact']:
        mask=d[label]
        if mask is None:out[label]=None;continue
        out[label]=dict(ground_count=int((gs&mask).sum()),all_ground_states=bool(mask[gs].all()),any_ground_state=bool(mask[gs].any()),lowest_energy_gap=float(E[mask].min()-e0) if mask.any() else None,lowest_failure_energy_gap=float(E[~mask].min()-e0) if (~mask).any() else None)
    legal=gs&d['feasible'];cost=d['cost'][legal]
    out['ground_feasible_original_cost_min']=float(cost.min()) if len(cost) else None
    out['ground_feasible_original_cost_max']=float(cost.max()) if len(cost) else None
    out['original_reference_cost']=d['f_star']
    out['ground_feasible_original_cost_gap_min']=float(cost.min()-d['f_star']) if len(cost) else None
    out['ground_feasible_original_cost_gap_max']=float(cost.max()-d['f_star']) if len(cost) else None
    cross=target_E[gs]-target_E.min()
    out['intended_energy_gap_of_minimizers']=dict(min=float(cross.min()),max=float(cross.max()),mean=float(cross.mean()))
    return out

def self_test():
    # Hand-checked two-bit unique minimum: E=-2a-b+4ab -> (1,0).
    z=states(2);E=energy(z,np.array([-2.,-1.]),np.array([[0.,4.],[4.,0.]]));assert E.tolist()==[0.,-2.,-1.,1.]
    # Two-customer assignment: both on one vehicle invalid under capacity1.
    I=dict(N=2,K=2,Q=1,q=[1,1],c=[[0,3],[3,0]],f_star=0)
    d=decode(z,I,'reduced');assert d['feasible'].tolist()==[False,True,True,False]
    # All 6-bit slack states: each feasible state requires split customers, exact slack0.
    zz=states(6);dd=decode(zz,I,'slack');assert dd['feasible'].sum()==8 and (dd['feasible']&dd['helper_exact']).sum()==2
    s=summarize(E,E,d,z);assert s['ground_state_count']==1 and s['feasible']['all_ground_states'] and s['next_distinct_energy_gap']==1
    near=np.array([0.,.5*TOL,2*TOL,1.]);ss=summarize(near,near,d,z);assert ss['ground_state_count']==2 and not ss['feasible']['all_ground_states'] and ss['feasible']['any_ground_state']
    return 5

def main(manifest):
    start=time.monotonic();test_count=self_test();data=json.loads(manifest.read_text());cases=data['cases'] if isinstance(data,dict) else data
    cache={};zcache={};dcache={};rows=[];skipped=[];evaluated=0;all_hamiltonians=set()
    for case in cases:
        npz_path=Path(case['npz_path'])
        if not npz_path.is_absolute():npz_path=HERE.parents[2]/npz_path
        model=np.load(npz_path);ht=model['h_target'];jt=model['J_target'];u=model['U'];n=len(ht)
        if n>20:continue
        I={k:case[k] for k in ['N','K','Q','q','c','f_star']};I['seed']=case.get('instance_seed');encoding=case['encoding'];ident=case.get('id',case.get('case_id'))
        assert jt.shape==u.shape==(n,n) and np.allclose(jt,jt.T) and np.allclose(u,u.T)
        assert np.all(np.diag(jt)==0) and np.all(np.diag(u)==0)
        if n not in zcache:zcache[n]=states(n)
        z=zcache[n];dk=json.dumps(dict(instance=I,encoding=encoding),sort_keys=True)
        if n>14:d=decode(z,I,encoding)
        else:
            if dk not in dcache:dcache[dk]=decode(z,I,encoding)
            d=dcache[dk]
        variants={'intended':(ht,jt),'pairs_only':(ht,u)}
        if len(model['h_actual']):variants['actual_endpoint']=(model['h_actual'],u)
        else:skipped.append(dict(id=ident,variant='actual_endpoint',reason='No saved actual endpoint fields'))
        energies={}
        for name,(h,j) in variants.items():
            sig=hashlib.sha256(np.ascontiguousarray(h,dtype='<f8').tobytes()+np.ascontiguousarray(j,dtype='<f8').tobytes()).hexdigest()
            if n>14:energies[name]=energy(z,h,j);evaluated+=len(z)
            else:
                if sig not in cache:cache[sig]=energy(z,h,j);evaluated+=len(z)
                energies[name]=cache[sig]
            all_hamiltonians.add(sig)
        result=dict(id=ident,tier=case.get('tier'),cohort=case.get('cohort'),encoding=encoding,atoms=n,instance_seed=case.get('instance_seed',I.get('seed')),embedder=case.get('embedder'),placement_seed=case.get('placement_seed'),controls=case.get('controls'),variants={name:summarize(E,energies['intended'],d,z) for name,E in energies.items()})
        rows.append(result)
        if n>14:print(f'Exact completed {ident}: {n} atoms, {len(variants)} variants',flush=True)
    out=dict(method='Exact exhaustive binary enumeration, independent literal upper-pair energy evaluation and decoder',ground_tie_absolute_tolerance=TOL,original_cost_tolerance=TOL,energy_convention='Physical energy coefficients; additive constants omitted; no rescaling or refitting',cases=len(rows),small_cases=sum(r['atoms']<=14 for r in rows),medium_20atom_cases=sum(r['atoms']==20 for r in rows),unique_hamiltonians=len(all_hamiltonians),unique_hamiltonian_state_evaluations=evaluated,self_tests_passed=test_count,seconds=time.monotonic()-start,skipped=skipped,rows=rows)
    (HERE/'small_results.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=HERE/'cases.json');p.add_argument('--test',action='store_true');args=p.parse_args()
    if args.test:print('Self checks passed:',self_test())
    else:main(args.manifest)
