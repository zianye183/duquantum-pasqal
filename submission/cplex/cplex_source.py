"""Independent constrained CPLEX models; no enumerated partition costs enter either model."""
import argparse
import itertools
import json
from pathlib import Path
import time
import cplex
import numpy as np
from pulser import Sequence
from baseline import (N, K, CAP, DEPOT, PAIRS, ALL_BITS, instance, qubo, energies,
                      decode, loads, cluster_cost, stamp, save_json, register_diagnostics)


def new_model():
    model = cplex.Cplex()
    model.set_log_stream(None); model.set_results_stream(None)
    model.set_warning_stream(None); model.set_error_stream(None)
    model.parameters.timelimit.set(30.)
    model.parameters.threads.set(1)
    model.parameters.randomseed.set(0)
    model.parameters.mip.tolerances.mipgap.set(0.)
    model.parameters.mip.tolerances.absmipgap.set(0.)
    model.objective.set_sense(model.objective.sense.minimize)
    return model


def add_binary(model, names, objective=None):
    model.variables.add(names=names, types='B'*len(names), obj=objective or [0.]*len(names))


def constraint(model, coefficients, sense, rhs):
    model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=list(coefficients), val=list(coefficients.values()))],
                                 senses=[sense], rhs=[rhs])


def assignments(model, inst):
    names = {(k,i): f'y_{k}_{i}' for k in range(K) for i in range(N)}
    add_binary(model, list(names.values()))
    for i in range(N):
        constraint(model, {names[k,i]: 1. for k in range(K)}, 'E', 1.)
    for k in range(K):
        constraint(model, {names[k,i]: float(inst['d'][i]) for i in range(N)}, 'L', CAP)
    return names


def solve(model):
    start = time.perf_counter(); model.solve(); elapsed = time.perf_counter()-start
    status = model.solution.get_status_string()
    if model.solution.get_status() != model.solution.status.MIP_optimal:
        raise RuntimeError(f'No proven optimum: {status}')
    return dict(status=status, objective=model.solution.get_objective_value(), solve_seconds=elapsed,
                relative_gap=model.solution.MIP.get_mip_relative_gap(),
                variables=model.variables.get_num(), constraints=model.linear_constraints.get_num())


def extract_assignment(model, y, inst):
    a = np.array([next(k for k in range(K) if model.solution.get_values(y[k,i]) > .5) for i in range(N)])
    assert all(sum(model.solution.get_values(y[k,i]) > .5 for k in range(K)) == 1 for i in range(N))
    assert loads(a, inst['d']).max() <= CAP
    return a


def clustering(inst):
    model = new_model(); y = assignments(model, inst)
    for k in range(K):
        for i,j in itertools.combinations(range(N),2):
            z=f'pair_{k}_{i}_{j}'
            add_binary(model,[z],[float(inst['c'][i,j])])
            constraint(model,{z:1.,y[k,i]:-1.},'L',0.)
            constraint(model,{z:1.,y[k,j]:-1.},'L',0.)
            constraint(model,{z:1.,y[k,i]:-1.,y[k,j]:-1.},'G',-1.)
    result=solve(model); a=extract_assignment(model,y,inst)
    assert abs(cluster_cost(a,inst['c'])-result['objective']) < 1e-7
    result.update(assignment=a, loads=loads(a,inst['d']), solution_validated=True)
    return result


def routing(inst):
    model=new_model(); y=assignments(model,inst)
    xy=np.vstack([DEPOT,inst['xy']]); distances=np.linalg.norm(xy[:,None]-xy[None,:],axis=-1)
    arcs={(k,i,j):f'a_{k}_{i}_{j}' for k in range(K) for i in range(N+1) for j in range(N+1) if i!=j}
    add_binary(model,list(arcs.values()),[float(distances[i,j]) for k,i,j in arcs])
    for k in range(K):
        # At most one depot departure; balanced depot returns. Unused trucks have zero arcs.
        constraint(model,{arcs[k,0,j]:1. for j in range(1,N+1)},'L',1.)
        balance={arcs[k,0,j]:1. for j in range(1,N+1)}
        balance.update({arcs[k,j,0]:-1. for j in range(1,N+1)})
        constraint(model,balance,'E',0.)
        for i in range(1,N+1):
            outgoing={arcs[k,i,j]:1. for j in range(N+1) if j!=i}; outgoing[y[k,i-1]]=-1.
            incoming={arcs[k,j,i]:1. for j in range(N+1) if j!=i}; incoming[y[k,i-1]]=-1.
            constraint(model,outgoing,'E',0.); constraint(model,incoming,'E',0.)
        # Complete customer-subset cuts exclude every depot-disconnected cycle.
        for size in range(2,N+1):
            for subset in itertools.combinations(range(1,N+1),size):
                constraint(model,{arcs[k,i,j]:1. for i in subset for j in subset if i!=j},'L',size-1.)
    result=solve(model); a=extract_assignment(model,y,inst)
    routes=[]; actual_cost=0.
    for k in range(K):
        selected={(i,j) for kk,i,j in arcs if kk==k and model.solution.get_values(arcs[kk,i,j])>.5}
        expected=set(np.flatnonzero(a==k)+1)
        if not expected:
            assert not selected; routes.append([]); continue
        tour=[]; visited_edges=set(); current=0
        while True:
            next_nodes=[j for i,j in selected if i==current]
            assert len(next_nodes)==1
            nxt=next_nodes[0]; edge=(current,nxt)
            assert edge not in visited_edges
            visited_edges.add(edge); actual_cost+=distances[current,nxt]
            if nxt==0: break
            assert nxt not in tour; tour.append(nxt); current=nxt
            assert len(tour)<=N
        assert set(tour)==expected and visited_edges==selected
        routes.append([int(i-1) for i in tour])
    assert abs(actual_cost-result['objective']) < 1e-7
    result.update(assignment=a, loads=loads(a,inst['d']), routes=routes, solution_validated=True)
    return result


def run(output):
    output=Path(output)
    records=[]; corrections=[]
    for seed in [12,14,16]:
        inst=instance(seed)
        cr=clustering(inst); vr=routing(inst)
        cr['brute_force_reference']=inst['model_reference']; vr['brute_force_reference']=inst['cvrp_reference']
        for result in (cr,vr):
            result['absolute_difference']=abs(result['objective']-result['brute_force_reference'])
            assert result['absolute_difference'] < 1e-7
        records.append(dict(seed=seed,clustering=cr,cvrp=vr))
        raw=json.loads((output/f'instance_{seed}.json').read_text())
        seq=Sequence.from_abstract_repr((output/f'sequence_{seed}.json').read_text())
        q,_,_=qubo(inst)
        diag,u=register_diagnostics(seq,q,raw['embedding']['alpha'],raw['embedding']['delta_final'],inst['d'])
        corrections.append(dict(seed=seed,original_embedding=raw['embedding'],actual_register_diagnostic=diag,
                                max_position_change_um=float(np.max(np.abs(np.asarray(raw['positions'])-np.array([v.as_array() for v in seq.register.qubits.values()]))))))
    save_json(output/'cplex_crosscheck.json',dict(completed_et=stamp(),cplex_version=cplex.__version__,
              settings=dict(time_limit_seconds=30,threads=1,randomseed=0,relative_mip_gap=0,absolute_mip_gap=0),
              provenance='Subsequent independent crosscheck. Original run manifest and results remain unchanged.',results=records))
    save_json(output/'register_rounding_diagnostics.json',dict(completed_et=stamp(),
              provenance='Recomputed from saved serialized sequence register. No physical samples rerun or modified. Original fit scale and pulse detuning retained.',results=corrections))
    print('PASS: six independent constrained optima match brute force; all solutions validated.')


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',default='experiments/track_a_baseline/results')
    run(p.parse_args().output)
