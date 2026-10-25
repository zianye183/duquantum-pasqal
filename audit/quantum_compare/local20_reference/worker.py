"""Official local SV reproduction of exact frozen cloud baselines, one CPU.
No cloud submissions. Cloud configuration changes only CPU selection and a local
state observable; underlying pulse, interactions and numerical defaults retained.
"""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import argparse,hashlib,json,time,traceback,importlib.metadata
import torch
import numpy as np
torch.set_num_threads(1)
from pulser import Sequence
from pulser.backend import EmulationConfig,StateResult
from emu_sv import SVBackend
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from formulations import classify_bits
HERE=Path(__file__).resolve().parent.parent

def run(name,dt):
    source=HERE/'ramp_remaining_prepared'/name;out=HERE/'local20_reference'/(name+'_dt'+str(dt));out.mkdir(parents=True,exist_ok=True)
    record=dict(id=name,status='running',configuration_changes=['gpu=False','additional local final-state observable','dt='+str(dt)+' ns'],dt_ns=dt,source_hashes={n:hashlib.sha256((source/(n+'.json')).read_bytes()).hexdigest() for n in ['sequence','config','metadata']})
    (out/'status.json').write_text(json.dumps(record,indent=2));start=time.monotonic()
    try:
        seq=Sequence.from_abstract_repr((source/'sequence.json').read_text());cfg=EmulationConfig.from_abstract_repr((source/'config.json').read_text());meta=json.loads((source/'metadata.json').read_text())
        assert len(seq.register.qubits)==20
        cfg=cfg.with_changes(dt=float(dt),gpu=False,observables=[*cfg.observables,StateResult(evaluation_times=[1.])])
        backend=SVBackend(seq,config=cfg);result=backend.run();counts=dict(result.get_result('bitstrings',1.));order=list(result.atom_order)
        (out/'counts.json').write_text(json.dumps(counts,indent=2));assert sum(counts.values())==meta['shots']
        logical=[f'q{i}' for i in range(20)];indices=[order.index(x) for x in logical]
        bits=np.array([[int(b[i]) for i in indices] for b in counts],dtype=np.int8);masks=classify_bits(bits,meta['target'],'reduced');weights=np.array(list(counts.values()))/sum(counts.values())
        scores={k:float(weights[v].sum()) for k,v in masks.items() if v.dtype==bool}
        state=result.get_result('state',1.)
        record.update(status='completed',counts=sum(counts.values()),atom_order=order,scores=scores,state_class=type(state).__name__,state_public_attributes=[x for x in dir(state) if not x.startswith('_')])
        # Inspect supported state object without assuming any state-vector convention.
        for attr in ['data','vector','state_vector','amplitudes']:
            if hasattr(state,attr):
                value=getattr(state,attr)
                if callable(value):continue
                if hasattr(value,'as_tensor'):value=value.as_tensor()
                if isinstance(value,torch.Tensor):value=value.detach().cpu().numpy()
                arr=np.asarray(value)
                if arr.size==1<<20 and np.issubdtype(arr.dtype,np.number):
                    np.savez_compressed(out/'raw_state.npz',state=arr)
                    record.update(raw_state_attribute=attr,raw_state_norm=float(np.vdot(arr.ravel(),arr.ravel()).real),state_conversion='Raw backend basis retained; do not treat as logical little-endian without conversion.')
                    record['eigenstates']=list(state.eigenstates)
                    assert tuple(state.eigenstates)==('r','g')
                    logical_indices=np.arange(1<<20,dtype=np.uint32)
                    raw_indices=np.zeros(1<<20,dtype=np.uint32)
                    for logical_i in range(20):
                        position=order.index(f'q{logical_i}')
                        raw_indices|=((logical_indices>>logical_i)&1)<<(19-position)
                    probabilities=abs(arr.ravel()[raw_indices])**2
                    np.savez_compressed(out/'logical_probabilities.npz',probabilities=probabilities)
                    logical_bits=((logical_indices[:,None]>>np.arange(20))&1).astype(np.int8)
                    exact_masks=classify_bits(logical_bits,meta['target'],'reduced')
                    record['exact_probability_scores']={k:float(probabilities[v].sum()) for k,v in exact_masks.items() if v.dtype==bool}
                    record['state_conversion']='Installed emu-sv2.10 data uses occupation bits (verified StateVector.from_state_amplitudes and sample); reversed/permuted to logical little-endian, no complement.'
                    break
    except Exception as exc:
        record.update(status='failed',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    record['seconds']=time.monotonic()-start
    record['versions']={x:importlib.metadata.version(x) for x in ['pulser','emu-sv','torch']}
    (out/'status.json').write_text(json.dumps(record,indent=2,allow_nan=False));print(json.dumps(record),flush=True)

if __name__=='__main__':
    run(sys.argv[1],int(sys.argv[2]))
