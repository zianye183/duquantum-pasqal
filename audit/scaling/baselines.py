"""Original-assignment random controls. No optimization references guide sampling."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time
from zoneinfo import ZoneInfo
import numpy as np
from references import score_counts


def reduced_bits(assignment, vehicles):
    return ''.join(str(int(a == k)) for a in assignment for k in range(1, vehicles))


def random_assignments(n, vehicles, instance_seed, repeat, method, samples=2000):
    if method not in ('uniform_assignment', 'balanced_cardinality'):
        raise ValueError('Unknown baseline method')
    method_id = 0 if method == 'uniform_assignment' else 1
    rng = np.random.default_rng(np.random.SeedSequence([int(instance_seed), int(repeat), method_id]))
    if method_id == 0:
        return rng.integers(0, vehicles, size=(samples, n))
    # Equal cardinalities up to the indivisible remainder, uniformly permuted.
    # Extra slots belong to the first labels; label names do not affect objectives.
    base = np.arange(n) % vehicles
    return np.asarray([rng.permutation(base) for _ in range(samples)])


def greedy_demand_first(demands, vehicles, capacity):
    """One pass, decreasing demand, choose least-loaded available vehicle.

    Ties use customer/vehicle index. No distances, references, repair or backtrack.
    Returns None if this greedy procedure fails, even if the instance is feasible.
    """
    loads=[0]*vehicles; assign=[-1]*len(demands)
    for customer in sorted(range(len(demands)), key=lambda i:(-demands[i],i)):
        choices=[k for k in range(vehicles) if loads[k]+demands[customer]<=capacity]
        if not choices: return None
        chosen=min(choices,key=lambda k:(loads[k],k))
        assign[customer]=chosen; loads[chosen]+=demands[customer]
    return assign


def run(instances_path, output):
    started=time.perf_counter(); rows=[]
    blob=Path(instances_path).read_bytes(); instances=json.loads(blob)['instances']
    for inst in instances:
        for method in ('uniform_assignment','balanced_cardinality'):
            for repeat in (0,1,2):
                before=time.perf_counter()
                assignments=random_assignments(inst['N'],inst['K'],inst['seed'],repeat,method)
                counts=Counter(reduced_bits(a,inst['K']) for a in assignments)
                digest=hashlib.sha256(json.dumps(sorted(counts.items()),separators=(',',':')).encode()).hexdigest()
                score=score_counts(counts,inst,'reduced')
                rows.append(dict(tier=inst['tier'],instance_seed=inst['seed'],method=method,
                    repeat_seed=repeat,samples=2000,unique_assignments=len(counts),
                    counts_sha256=digest,score=score,seconds=time.perf_counter()-before))
        before=time.perf_counter()
        assignment=greedy_demand_first(inst['q'],inst['K'],inst['Q'])
        score=score_counts({reduced_bits(assignment,inst['K']):1} if assignment is not None else {},inst,'reduced')
        rows.append(dict(tier=inst['tier'],instance_seed=inst['seed'],method='greedy_demand_first',
            repeat_seed=None,samples=1,assignment=assignment,success=assignment is not None,
            score=score,seconds=time.perf_counter()-before,
            budget_note='One deterministic solution attempt; not a 2000-sample comparator'))
        print(inst['tier'],inst['seed'],'complete',flush=True)
    result=dict(rows=rows,instances_sha256=hashlib.sha256(blob).hexdigest(),numpy_version=np.__version__,
        protocol=dict(samples_per_random_repeat=2000,repeat_seeds=[0,1,2],
            seed_construction='numpy SeedSequence([instance_seed, repeat_seed, method_id]); uniform=0 balanced=1',
            assignment_domain='Original vehicle labels, no redundant encoding states sampled',
            balanced_definition='Each group has floor(N/K) or ceil(N/K) customers; random permutations, not demand balancing',
            optimization_references='Evaluation only; never used in candidate generation',
            raw_counts='Reproducible from seeds and generator; canonical count-list SHA256 retained',
            comparison_limit='Random assignment budgets match 2000 outputs, not time or quantum state preparation effort'),
        completed_et=datetime.now(ZoneInfo('America/New_York')).isoformat(),seconds=time.perf_counter()-started)
    Path(output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--instances',default='audit/scaling/references/instances.json')
    parser.add_argument('--output',default='audit/scaling/references/baselines.json')
    args=parser.parse_args();run(args.instances,args.output)
