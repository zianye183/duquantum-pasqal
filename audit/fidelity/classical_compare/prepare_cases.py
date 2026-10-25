"""Freeze classical diagonal-energy comparisons from existing saved experiments."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.spatial.distance import cdist
from pulser import Sequence
from pulser.sampler import sample

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    rows=json.loads((ROOT/'audit/fidelity/recomputed/runs.json').read_text())
    rows=[r for r in rows if r['cohort'] in ['primary','transferred_penalties'] and '_accuracy' not in r['id']]
    instances={(i['tier'],i['seed']):i for i in json.loads((ROOT/'audit/scaling/references/instances.json').read_text())['instances']}
    # Selection depends only on design identifiers, never solver outcomes/readiness.
    first={}
    for r in rows:
        key=(r['cohort'],r['tier'],r['encoding'],r['embedder'])
        first[key]=min(first.get(key,r['instance_seed']),r['instance_seed'])
    selected=[r for r in rows if r['tier']=='S' or (r['tier']=='M' and r['placement_seed']==0) or
              (r['tier']=='L' and r['placement_seed']==0 and r['instance_seed']==first[(r['cohort'],r['tier'],r['encoding'],r['embedder'])])]
    (OUT/'cases').mkdir(parents=True,exist_ok=True)
    cases=[]
    for r in sorted(selected,key=lambda r:({'S':0,'M':1,'L':2}[r['tier']],r['id'])):
        source=ROOT/r['pair_artifact'];data=np.load(source)
        J=data['J'];h=data['h'];n=len(h);a=float(data['alpha']);positions=data['positions'];c6=float(data['c6'])
        pre='prepared' if r['cohort']=='primary' else 'transferred_prepared'
        cloud='cloud_results' if r['cohort']=='primary' else 'transferred_cloud_results'
        sp=ROOT/'audit/scaling'/cloud/r['id']/'submitted_sequence.json'
        if not sp.exists():sp=ROOT/'audit/scaling'/pre/r['id']/'sequence.json'
        actual=np.array([]);amp=np.array([]);sequence_hash=None
        if sp.exists():
            seq=Sequence.from_abstract_repr(sp.read_text());reg={str(k):np.asarray(v,float) for k,v in seq.register.qubits.items()}
            order=['q'+str(k) for k in range(n)]
            if set(order)!=set(reg):
                order=[str(k) for k in range(n)]
            assert set(order)==set(reg)
            p=np.array([reg[k] for k in order]);assert np.array_equal(p,positions)
            assert float(seq.device.interaction_coeff)==c6
            wave=sample(seq).to_nested_dict(all_local=True)['Local']['ground-rydberg'];wave={str(k):v for k,v in wave.items()}
            actual=np.array([-float(wave[k]['det'][-1]) for k in order])
            amp=np.array([float(wave[k]['amp'][-1]) for k in order]);sequence_hash=digest(sp)
            assert sequence_hash==r['sequence_sha256']
        d=np.round(cdist(positions,positions),6);np.fill_diagonal(d,np.inf)
        U=c6/d**6
        ht=a*h;Jt=a*J
        assert np.allclose(U,U.T) and np.all(np.diag(U)==0)
        path=OUT/'cases'/(r['id']+'.npz')
        np.savez_compressed(path,h_target=ht,J_target=Jt,U=U,h_actual=actual,endpoint_amplitude=amp,alpha=a)
        I=instances[(r['tier'],r['instance_seed'])]
        c={k:r[k] for k in ['id','cohort','tier','encoding','embedder','instance_seed','placement_seed','controls','atoms','preparation_status','coordinate_source','relative_error_recorded']}
        c.update({k:I[k] for k in ['N','K','Q','q','c','f_star']})
        c.update(npz_path=str(path.relative_to(ROOT)),npz_sha256=digest(path),source_pair_sha256=digest(source),sequence_path=str(sp.relative_to(ROOT)) if sp.exists() else None,
                 sequence_sha256=sequence_hash,alpha=a,actual_endpoint_available=bool(actual.size),max_endpoint_amplitude=float(np.max(np.abs(amp))) if amp.size else None,
                 reference_status=I['reference_status'],reference_partition=I['model_partition'])
        cases.append(c)
    protocol=dict(selection='All main small cases; every medium instance/method/cohort at placement0; large first instance within cohort/encoding/method at placement0. Retain both saved control modes; deduplicate numerical solves by coefficients.',
        variants={'intended':'alpha*h, alpha*J','pairs_only':'alpha*h, U from rounded geometric distances','actual_endpoint':'negative actual endpoint detunings, U'},
        coefficient_convention='E=sum(h_i*x_i)+sum(i<j,J_ij*x_i*x_j); symmetric J stores full unordered-pair coefficients; constants dropped in all variants',
        quantum_caveat='Classical diagonal endpoint energy only; transverse drive amplitudes recorded, no time-evolution claim',
        large_time_limit_seconds=10,small_tie_tolerance=1e-8,cloud_submissions=0,
        counts={t:sum(c['tier']==t for c in cases) for t in ['S','M','L']},cases=cases)
    (OUT/'cases.json').write_text(json.dumps(protocol,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in protocol.items() if k!='cases'},indent=2))
if __name__=='__main__':main()
