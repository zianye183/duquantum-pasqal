import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import torch
import numpy as np
import json
from pathlib import Path
from emu_sv import StateVector
torch.set_num_threads(1)
n=20;rows=[]
for atom in [0,1,19]:
 label=''.join('r' if i==atom else 'g' for i in range(n));st=StateVector.from_state_amplitudes(eigenstates=('r','g'),amplitudes={label:1.});arr=st.data.cpu().numpy();raw=int(np.argmax(abs(arr)));expected=1<<(n-1-atom);assert raw==expected
 samples=dict(st.sample(num_shots=10));wanted=''.join('1' if i==atom else '0' for i in range(n));assert samples=={wanted:10}
 logical=sum(int(v)<<i for i,v in enumerate(wanted));assert logical==1<<atom
 restored=sum(((logical>>i)&1)<<(n-1-i) for i in range(n));assert restored==raw
 rows.append(dict(atom=atom,raw_index=raw,logical_index=logical,counts=samples,passed=True))
result=dict(passed=True,atoms=n,tests=rows,aborted_attempt='Initial adaptation retained a14-bit shift constant; stopped before scientific output, corrected to20-bit shift. Approximately40seconds preliminary work retained in aborted_preflight_conversion_fix.')
Path(__file__).with_name('basis_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
