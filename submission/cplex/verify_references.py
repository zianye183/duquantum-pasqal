import ast,json,itertools,time
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import cplex
HERE=Path(__file__).resolve().parent
source=HERE/'cplex_source.py'
ns=dict(cplex=cplex,np=np,time=time,itertools=itertools,N=4,K=2,CAP=7,DEPOT=np.array([50.,50.]))
ns['loads']=lambda a,q:np.array([q[a==k].sum() for k in range(2)])
ns['cluster_cost']=lambda a,c:float(sum(c[i,j] for i,j in itertools.combinations(range(4),2) if a[i]==a[j]))
for node in ast.parse(source.read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['new_model','add_binary','constraint','assignments','solve','extract_assignment','clustering','routing']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
instances=json.loads((HERE.parents[1]/'audit/scaling/references/instances.json').read_text())['instances'];rows=[]
for I in instances:
 if I['tier']!='S':continue
 inst={'d':np.array(I['q']),'xy':np.array(I['xy']),'c':np.array(I['c'])}
 row={'seed':I['seed']}
 for label,fn,ref in [('clustering','clustering',I['f_star']),('cvrp','routing',I['cvrp_ref'])]:
  r=ns[fn](inst);diff=abs(r['objective']-ref);assert diff<1e-7
  row[label]={**r,'reference':ref,'absolute_difference':diff}
 rows.append(row)
out={'completed_et':datetime.now(ZoneInfo('America/New_York')).isoformat(),'cplex_version':cplex.__version__,'settings':{'time_limit_seconds':30,'threads':1,'seed':0,'relative_mip_gap':0,'absolute_mip_gap':0},'results':rows,'passed':True}
(HERE/'cplex_scaling_small.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x))
print('PASS: 20 constrained CPLEX solves match all 10 small clustering and CVRP references.')
