"""Exact exponential evaluation references, NEVER optimizer inputs. N <= 15."""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np

TIERS = {'S': (4, 2, 7, 4), 'M': (10, 3, 20, 8), 'L': (15, 4, 30, 10)}
TOL = 1e-8

def make_candidate(tier, seed):
    n, k, cap, top = TIERS[tier]
    rng = np.random.default_rng(seed)
    return dict(seed=seed, tier=tier, coordinates=rng.uniform(0, 100, (n, 2)).tolist(),
                demands=rng.integers(1, top + 1, n).tolist(), capacity=cap,
                vehicles=k, depot=[50., 50.])

def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit

def tables(xy, demands, depot, capacity):
    """Held-Karp paths from depot ending at customer, all capacity-feasible subsets."""
    n = len(demands); size = 1 << n
    dist = np.linalg.norm(xy[:, None] - xy[None, :], axis=-1)
    radial = np.linalg.norm(xy - depot, axis=1)
    loads = np.zeros(size, dtype=int); pair = np.zeros(size)
    paths = np.full((size, n), np.inf); tours = np.full(size, np.inf); tours[0] = 0.
    for mask in range(1, size):
        b = mask & -mask; i = b.bit_length() - 1; rest = mask ^ b
        loads[mask] = loads[rest] + demands[i]
        pair[mask] = pair[rest] + sum(dist[i, j] for j in members(rest))
        if loads[mask] > capacity: continue
        if not rest:
            paths[mask, i] = radial[i]
        else:
            for j in members(mask):
                prev = mask ^ (1 << j)
                paths[mask, j] = min(paths[prev, i] + dist[i, j] for i in members(prev))
        tours[mask] = min(paths[mask, j] + radial[j] for j in members(mask))
    return loads, pair, tours

def partition_dp(loads, costs, capacity, vehicles):
    """Anchor smallest remaining customer to count each unlabeled partition once.

    Every recursion uses exactly g nonempty groups. The final minimum over
    1..vehicles explicitly allows unused vehicles. Counts include numerical ties
    within absolute TOL, with no relative tolerance.
    """
    transitions = 0
    @lru_cache(None)
    def solve(mask, g):
        nonlocal transitions
        if not mask: return (0., 1, ()) if g == 0 else (float('inf'), 0, ())
        if g <= 0 or mask.bit_count() < g or loads[mask] > g * capacity:
            return float('inf'), 0, ()
        if g == 1:
            return (float(costs[mask]), 1, (mask,)) if loads[mask] <= capacity else (float('inf'), 0, ())
        anchor = mask & -mask; free = mask ^ anchor; sub = free
        best = float('inf'); count = 0; chosen = ()
        while True:
            group = sub | anchor; remainder = mask ^ group
            if loads[group] <= capacity and remainder.bit_count() >= g - 1:
                transitions += 1
                tail, ways, groups = solve(remainder, g - 1)
                value = float(costs[group]) + tail
                if ways:
                    if value < best:
                        best, count, chosen = value, 1, (group,) + groups
            if sub == 0: break
            sub = (sub - 1) & free
        return best, count, chosen
    @lru_cache(None)
    def count_with_budget(mask, g, budget):
        # Apply tolerance to the WHOLE partition, never once per recursion level.
        minimum, feasible, _ = solve(mask, g)
        if not feasible or minimum > budget: return 0
        if g <= 1: return 1
        anchor = mask & -mask; free = mask ^ anchor; sub = free; total = 0
        while True:
            group = sub | anchor; remainder = mask ^ group
            if loads[group] <= capacity and remainder.bit_count() >= g - 1:
                total += count_with_budget(remainder, g - 1, budget - float(costs[group]))
            if sub == 0: break
            sub = (sub - 1) & free
        return total
    full = len(loads) - 1
    answers = [solve(full, g) for g in range(1, min(vehicles, full.bit_count()) + 1)]
    best = min(a[0] for a in answers)
    optimal = [a for a in answers if a[1] and abs(a[0] - best) <= TOL]
    chosen = min(optimal, key=lambda a:a[0])[2] if optimal else ()
    return dict(objective=best if optimal else None,
                distinct_optima=sum(count_with_budget(full, g, best + TOL) for g in range(1, min(vehicles, full.bit_count()) + 1)) if optimal else 0,
                groups=[list(members(mask)) for mask in chosen],
                states=solve.cache_info().currsize, transitions=transitions)

def evaluate(instance):
    started = time.perf_counter(); data = dict(instance)
    xy=np.asarray(data['coordinates'],float); d=np.asarray(data['demands'],int)
    cap=data['capacity']; k=data['vehicles']; n=len(d)
    if not (1 <= n <= 15) or xy.shape != (n,2): raise ValueError('Expected 1..15 customers')
    if not np.isfinite(xy).all() or np.any(d <= 0) or not np.array_equal(d,data['demands']):
        raise ValueError('Coordinates must be finite and demands positive integers')
    if cap <= 0 or k <= 0: raise ValueError('Capacity and vehicles must be positive')
    loads,pair,tours=tables(xy,d,np.asarray(data['depot'],float),cap)
    table_seconds=time.perf_counter()-started
    t=time.perf_counter(); model=partition_dp(loads,pair,cap,k); model_seconds=time.perf_counter()-t
    if model['objective'] is None:
        return dict(**data,feasible=False,certificate=None,reference_status='proven_infeasible_subset_partition_dp',
                    runtimes=dict(tables_seconds=table_seconds,model_seconds=model_seconds,total_seconds=time.perf_counter()-started))
    t=time.perf_counter(); routed=partition_dp(loads,tours,cap,k); route_seconds=time.perf_counter()-t
    cert=[-1]*n
    for label,group in enumerate(model['groups']):
        for i in group: cert[i]=label
    data.update(feasible=True,certificate=cert,model_reference=model['objective'],cvrp_reference=routed['objective'],
                distinct_model_optima=model['distinct_optima'],model_partition=model['groups'],cvrp_partition=routed['groups'],
                reference_status='proven_exact_subset_dynamic_programming',
                counts=dict(subsets=1<<n,feasible_nonempty_subsets=int(np.count_nonzero(loads[1:]<=cap)),
                            model_states=model['states'],model_transitions=model['transitions'],
                            cvrp_states=routed['states'],cvrp_transitions=routed['transitions']),
                runtimes=dict(tables_seconds=table_seconds,model_seconds=model_seconds,cvrp_seconds=route_seconds,
                              total_seconds=time.perf_counter()-started))
    return data

def first_feasible_packing(demands, vehicles, capacity):
    """First lexicographic feasible assignment; only capacity/demands enter.

    Demand order and vehicle order are fixed; equivalent equal-load vehicle
    branches are skipped. No distances, clustering scores or reference answers
    are consulted. Returns None when capacity packing is impossible.
    """
    q=tuple(int(v) for v in demands)
    if vehicles < 1 or capacity < 1 or any(v <= 0 for v in q):
        raise ValueError('Positive demands, capacity and vehicle count required')
    loads=[0]*vehicles; assignment=[0]*len(q)
    def search(index):
        if index==len(q): return tuple(assignment)
        tried=set()
        for group in range(vehicles):
            if loads[group] in tried or loads[group]+q[index]>capacity: continue
            tried.add(loads[group]); loads[group]+=q[index]; assignment[index]=group
            answer=search(index+1)
            loads[group]-=q[index]
            if answer is not None: return answer
        return None
    if sum(q)>vehicles*capacity or max(q,default=0)>capacity: return None
    result=search(0)
    return list(result) if result is not None else None


def make_instance(tier, seed):
    """Independent draw; reject whole seed only for feasibility or inactive capacity.

    Numerical equality uses absolute 1e-8, relative zero; this is numerical tolerance,
    not a nonzero permitted optimization gap. References are evaluation-only.
    """
    raw = make_candidate(tier, seed)
    result = evaluate(raw)
    if not result['feasible']:
        return None
    xy=np.asarray(raw['coordinates']); q=np.asarray(raw['demands']); n=len(q)
    loads,pair,tours=tables(xy,q,np.asarray(raw['depot']),raw['capacity'])
    free=partition_dp(loads,pair,int(q.sum()),raw['vehicles'])
    if result['model_reference'] <= free['objective'] + TOL:
        return None
    return dict(tier=tier,seed=int(seed),N=n,K=raw['vehicles'],Q=raw['capacity'],
        q=q.tolist(),xy=xy.tolist(),depot=raw['depot'],
        c=np.linalg.norm(xy[:,None]-xy[None,:],axis=-1).tolist(),
        f_star=result['model_reference'],cvrp_ref=result['cvrp_reference'],
        certificate_feasible_only=first_feasible_packing(q,raw['vehicles'],raw['capacity']),
        certificate_role='evaluation_only_exact_clustering_witness',
        unconstrained_f_star=free['objective'],certificate=result['certificate'],
        reference_status=result['reference_status'],capacity_active=True,
        distinct_model_optima=result['distinct_model_optima'],
        model_partition=result['model_partition'],cvrp_partition=result['cvrp_partition'],
        tour_costs=[float(v) if np.isfinite(v) else None for v in tours],
        reference_counts=result['counts'],reference_runtimes=result['runtimes'])


def generate_instance(tier, seed):
    return make_instance(tier, seed)


def slack_weights(capacity):
    width=int(np.ceil(np.log2(capacity+1)))
    weights=[1<<i for i in range(width)]
    weights[-1]=capacity-sum(weights[:-1])
    return weights


def score_counts(counts, I, encoding='reduced'):
    """No repair, exact optimal clustering with absolute numerical tolerance only.

    Counts must already be reordered into logical-variable order by the caller.
    CVRP cost optimizes each sampled feasible cluster route exactly; it does not
    silently replace the sampled clustering. Rates use ALL shots as denominator.
    """
    n,k,cap=I['N'],I['K'],I['Q']; q=np.asarray(I['q']); c=np.asarray(I['c'])
    if encoding not in ('reduced','slack'): raise ValueError('Unknown encoding')
    weights=slack_weights(cap); width=len(weights)
    expected=n*(k-1) if encoding=='reduced' else n*k+k*width
    shots=valid=feasible=optimal=slack_exact=route_optimal=0
    best_f=best_route=float('inf'); best_assign=None; feasible_candidates=[]
    for bits,cnt in counts.items():
        if not isinstance(bits,str) or len(bits)!=expected or set(bits)-{'0','1'}:
            raise ValueError('Bitstrings must have exact logical-variable length')
        if int(cnt)!=cnt or cnt<0: raise ValueError('Counts must be nonnegative integers')
        cnt=int(cnt)
        if not cnt: continue
        shots+=cnt; z=np.fromiter(map(int,bits),dtype=int)
        if encoding=='reduced':
            x=z.reshape(n,k-1)
            if np.any(x.sum(1)>1): continue
            assign=np.where(x.any(1),x.argmax(1)+1,0)
        else:
            x=z[:n*k].reshape(k,n)
            if np.any(x.sum(0)!=1): continue
            assign=x.argmax(0)
        valid+=cnt
        load=np.bincount(assign,weights=q,minlength=k).astype(int)
        if np.any(load>cap): continue
        feasible+=cnt
        if encoding=='slack':
            slack=z[n*k:].reshape(k,width)@np.asarray(weights)
            slack_exact+=cnt*bool(np.all(load+slack==cap))
        f=float(np.triu(c*(assign[:,None]==assign[None,:]),1).sum())
        if f < I['f_star']-TOL: raise AssertionError('Sample beats exact clustering reference')
        optimal+=cnt*bool(abs(f-I['f_star'])<=TOL)
        masks=[sum(1<<i for i in np.flatnonzero(assign==g)) for g in range(k)]
        route=sum(I['tour_costs'][int(mask)] for mask in masks)
        if route < I['cvrp_ref']-TOL: raise AssertionError('Sample beats exact CVRP reference')
        route_optimal+=cnt*bool(abs(route-I['cvrp_ref'])<=TOL)
        best_route=min(best_route,route)
        best_f=min(best_f,f)
        feasible_candidates.append((f,float(route),tuple(int(v) for v in assign)))
    selected_route=selected_f=float('inf')
    if feasible_candidates:
        selected_f,selected_route,chosen=min(
            (item for item in feasible_candidates if item[0]<=best_f+TOL),
            key=lambda item:(item[1],item[2]))
        best_assign=list(chosen)
    def gap(value,reference):
        if not np.isfinite(value): return None
        return 100*(value-reference)/reference if reference else (0. if abs(value)<=TOL else None)
    return dict(shots=shots,valid_code_count=valid,feasible_count=feasible,
        optimal_clustering_count=optimal,optimal_cvrp_count=route_optimal,
        valid_code_rate=valid/shots if shots else None,
        feasibility_rate=feasible/shots if shots else None,
        optimal_clustering_rate=optimal/shots if shots else None,
        optimal_cvrp_rate=route_optimal/shots if shots else None,
        slack_exact_count=slack_exact if encoding=='slack' else None,
        slack_exact_rate=slack_exact/shots if shots and encoding=='slack' else None,
        best_feasible_f=best_f if np.isfinite(best_f) else None,
        best_feasible_cvrp=best_route if np.isfinite(best_route) else None,
        model_gap_pct=gap(best_f,I['f_star']),cvrp_gap_pct=gap(best_route,I['cvrp_ref']),
        best_clustering_cvrp=selected_route if np.isfinite(selected_route) else None,
        best_clustering_cvrp_gap_pct=gap(selected_route,I['cvrp_ref']),
        selected_clustering_f=selected_f if np.isfinite(selected_f) else None,
        best_assignment=best_assign,epsilon_gap_pct=0,absolute_numeric_tolerance=TOL)


def run(output):
    start=time.perf_counter(); accepted=[]; rejected=[]
    for tier,number in [('S',10),('M',5),('L',5)]:
        seed=2000; count=0
        while count<number:
            result=make_instance(tier,seed)
            print(tier,seed,'accepted' if result else 'rejected',flush=True)
            if result is not None: accepted.append(result); count+=1
            else: rejected.append(dict(tier=tier,seed=seed,reason='infeasible_or_capacity_inactive'))
            seed+=1
    artifact=dict(instances=accepted,rejected_draws=rejected,
        method='Held-Karp subset tours; anchored subset partition DP; unused vehicles allowed',
        evaluation_only=True,settings=dict(max_customers=15,absolute_tie_tolerance=TOL,relative_tie_tolerance=0,epsilon_gap_pct=0),
        generator='numpy.default_rng(seed): uniform [0,100) coordinates then inclusive integer demands; whole-seed rejection for infeasibility or inactive capacity only',
        selection='First 10 S, 5 M, 5 L qualifying seeds starting at 2000 per tier; no solver outcome selection',
        numpy_version=np.__version__,completed_et=datetime.now(ZoneInfo('America/New_York')).isoformat(),
        total_seconds=time.perf_counter()-start)
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',default='audit/scaling/references/instances.json')
    run(parser.parse_args().output)
