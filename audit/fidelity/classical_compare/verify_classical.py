"""Independent full-matrix enumeration and direct decoder; no solver imports."""
from pathlib import Path
import json,time,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];TOL=1e-8

def enumerate_min(h,J):
    n=len(h);best=np.inf;solutions=[]
    for start in range(0,1<<n,65536):
        ix=np.arange(start,min(start+65536,1<<n),dtype=np.uint32)
        z=((ix[:,None]>>np.arange(n-1,-1,-1))&1).astype(float)
        e=z@h+.5*np.sum((z@J)*z,axis=1);minimum=float(e.min())
        if minimum<best-TOL:best=minimum;solutions=[]
        elif minimum<best:best=minimum
        for b,v in zip(z[abs(e-best)<=TOL],e[abs(e-best)<=TOL]):
            solutions.append((''.join(str(int(t)) for t in b),float(v)))
    return best,{b for b,e in solutions if abs(e-best)<=TOL}

def classify(bits,c):
    b=[int(x) for x in bits];N,K=c['N'],c['K'];assign=[]
    for i in range(N):
        if c['encoding']=='slack':chosen=[k for k in range(K) if b[k*N+i]]
        else:
            chosen=[k+1 for k in range(K-1) if b[i*(K-1)+k]]
            if not chosen:chosen=[0]
        if len(chosen)!=1:return False,False
        assign.append(chosen[0])
    loads=[sum(c['q'][i] for i in range(N) if assign[i]==k) for k in range(K)]
    feasible=max(loads)<=c['Q'];cost=sum(c['c'][i][j] for i in range(N) for j in range(i+1,N) if assign[i]==assign[j])
    return feasible,feasible and abs(cost-c['f_star'])<=TOL

def main():
    start=time.monotonic();manifest=json.loads((HERE/'cases.json').read_text());cases={c['id']:c for c in manifest['cases']}
    small=json.loads((HERE/'small_results.json').read_text());cache={};checks=0
    def solve(h,J):
        key=hashlib.sha256(h.tobytes()+J.tobytes()).hexdigest()
        if key not in cache:cache[key]=enumerate_min(h,J)
        return cache[key]
    for row in small['rows']:
        c=cases[row['id']];m=np.load(ROOT/c['npz_path'])
        for name,result in row['variants'].items():
            h=m['h_actual'] if name=='actual_endpoint' else m['h_target'];J=m['J_target'] if name=='intended' else m['U']
            best,bits=solve(h,J);assert abs(best-result['ground_energy'])<TOL
            assert bits==set(result['minimizer_bits']),(row['id'],name)
            scores=[classify(b,c) for b in bits]
            assert sum(s[0] for s in scores)==result['feasible']['ground_count']
            assert sum(s[1] for s in scores)==result['optimal']['ground_count'];checks+=1
    medium=[]
    for ident in ['M_2002_reduced_blade_0','M_2002_reduced_custom_0']:
        c=cases[ident];m=np.load(ROOT/c['npz_path'])
        for name in ['intended','pairs_only','actual_endpoint']:
            h=m['h_actual'] if name=='actual_endpoint' else m['h_target'];J=m['J_target'] if name=='intended' else m['U'];best,bits=solve(h,J)
            scores=[classify(b,c) for b in bits];medium.append(dict(id=ident,variant=name,exact_minimum=best,minimizer_bits=sorted(bits),minimizers=len(bits),feasible_minimizers=sum(s[0] for s in scores),optimal_minimizers=sum(s[1] for s in scores)))
    large=json.loads((HERE/'large_results.json').read_text())['results'];comparison=[]
    for exact in medium:
        matched=[r for r in large if r['case_id']==exact['id'] and r['variant']==exact['variant']]
        for r in matched:
            gap=r['objective']-exact['exact_minimum'];assert gap>=-TOL
            if r['certified_optimal']:assert abs(gap)<TOL
            comparison.append(dict(id=exact['id'],variant=exact['variant'],milp_status=r['status'],gap_to_exhaustive=gap))
    out=dict(exhaustive_case_variant_checks=checks,exhaustive_checks_passed=True,
             checked_cases_by_atoms={str(n):sum(r['atoms']==n for r in small['rows']) for n in sorted({r['atoms'] for r in small['rows']})},
             medium_exact_checks=medium,milp_comparisons=comparison,unique_enumerations=len(cache),seconds=time.monotonic()-start,method='Full symmetric quadratic matrix evaluation, big-endian enumeration, independent per-customer membership decoding; no solver/production scorer imports')
    (HERE/'evidence.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='medium_exact_checks'},indent=2))

if __name__=='__main__':main()
