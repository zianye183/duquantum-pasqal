"""Independently rescore a fixed canonical CSV snapshot; no analyzer/scorer imports.

The verifier reads raw counts from the chosen canonical source. Geometry and reference optimality proofs are outside scope. Routing costs use
stored exact subset-tour references, with independently constructed cluster subsets. Euclidean clustering costs are
recomputed from coordinates, not from the scorer's cached distance matrix.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,json,math,time,hashlib
ROOT=Path(__file__).resolve().parent
TOL=1e-8

def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def number(value):return None if value in (None,'','nan','None') else float(value)

def evaluate(raw,order,I,encoding):
    n,k,cap=I['N'],I['K'],I['Q'];width=math.ceil(math.log2(cap+1))
    expected=n*(k-1) if encoding=='reduced' else n*k+k*width
    assert len(order)==expected and len(set(order))==expected
    assert set(order)=={f'q{i}' for i in range(expected)}
    positions={label:index for index,label in enumerate(order)}
    distances={(i,j):math.hypot(I['xy'][i][0]-I['xy'][j][0],I['xy'][i][1]-I['xy'][j][1]) for i in range(n) for j in range(i+1,n)}
    weights=[2**b for b in range(width-1)];weights.append(cap-sum(weights))
    totals=dict(shots=0,valid_code_count=0,feasible_count=0,optimal_clustering_count=0,slack_exact_count=0,optimal_cvrp_count=0)
    best=None;cost_cache={};best_route=None;feasible_candidates=[]
    for bits,count in raw.items():
        assert isinstance(bits,str) and len(bits)==expected and not(set(bits)-{'0','1'})
        assert isinstance(count,int) and not isinstance(count,bool) and count>=0
        totals['shots']+=count
        if not count:continue
        z=[int(bits[positions[f'q{i}']]) for i in range(expected)]
        assignment=[];valid=True
        for customer in range(n):
            if encoding=='reduced':
                labels=[group+1 for group in range(k-1) if z[customer*(k-1)+group]]
                if len(labels)>1:valid=False;break
                assignment.append(labels[0] if labels else 0)
            else:
                labels=[group for group in range(k) if z[group*n+customer]]
                if len(labels)!=1:valid=False;break
                assignment.append(labels[0])
        if not valid:continue
        totals['valid_code_count']+=count
        loads=[sum(I['q'][i] for i in range(n) if assignment[i]==group) for group in range(k)]
        if any(load>cap for load in loads):continue
        totals['feasible_count']+=count
        if encoding=='slack' and all(loads[g]+sum(weights[b]*z[n*k+g*width+b] for b in range(width))==cap for g in range(k)):
            totals['slack_exact_count']+=count
        key=tuple(assignment)
        if key not in cost_cache:cost_cache[key]=math.fsum(value for (i,j),value in distances.items() if assignment[i]==assignment[j])
        cost=cost_cache[key];assert cost>=I['f_star']-TOL
        best=cost if best is None else min(best,cost)
        totals['optimal_clustering_count']+=count*(abs(cost-I['f_star'])<=TOL)
        subsets=[sum(2**i for i in range(n) if assignment[i]==group) for group in range(k)]
        route=math.fsum(I['tour_costs'][subset] for subset in subsets)
        assert route>=I['cvrp_ref']-TOL
        totals['optimal_cvrp_count']+=count*(abs(route-I['cvrp_ref'])<=TOL)
        best_route=route if best_route is None else min(best_route,route)
        feasible_candidates.append((cost,route,tuple(assignment)))
    totals['invalid_assignment_count']=totals['shots']-totals['valid_code_count']
    for rate,count in [('valid_code_rate','valid_code_count'),('feasibility_rate','feasible_count'),('optimal_clustering_rate','optimal_clustering_count'),('optimal_cvrp_rate','optimal_cvrp_count')]:totals[rate]=totals[count]/totals['shots']
    totals['slack_exact_rate']=totals['slack_exact_count']/totals['shots'] if encoding=='slack' else None
    totals['best_feasible_f']=best
    def gap(value,ref):return None if value is None else (100*(value-ref)/ref if ref else (0. if abs(value)<=TOL else None))
    totals['model_gap_pct']=gap(best,I['f_star'])
    totals['best_feasible_cvrp']=best_route;totals['cvrp_gap_pct']=gap(best_route,I['cvrp_ref'])
    selected=min((item for item in feasible_candidates if item[0]<=best+TOL),key=lambda item:(item[1],item[2])) if feasible_candidates else (None,None,None)
    totals['selected_clustering_f']=selected[0];totals['best_clustering_cvrp']=selected[1]
    totals['best_clustering_cvrp_gap_pct']=gap(selected[1],I['cvrp_ref'])
    totals['best_assignment']=list(selected[2]) if selected[2] is not None else None
    return totals

def run():
    started=time.perf_counter();ledger_paths=[ROOT/'analysis/scientific_conditions.csv',ROOT/'analysis/transferred_scientific_conditions.csv']
    ledger_hashes={str(p):digest(p) for p in ledger_paths}
    rows=[]
    for path in ledger_paths:
        with path.open() as f:rows+=list(csv.DictReader(f))
    assert len({r['id'] for r in rows})==len(rows)
    by_id={r['id']:r for r in rows}
    instances={(r['tier'],r['seed']):r for r in read(ROOT/'references/instances.json')['instances']}
    retries=read(ROOT/'cloud_checks/official_retries/RETRIES.json')['retries']
    def locate(row):
        alias=row.get('alias_of')
        if alias and alias not in ('nan','None'):return locate(by_id[alias])
        transfer=row['cohort'].startswith('transferred')
        source=row['result_source']
        if source=='pasqal_cloud':return ROOT/('transferred_cloud_results' if transfer else 'cloud_results')/row['id']
        if source=='local_cpu_fallback':return ROOT/('transferred_local_results' if transfer else 'local_results')/row['id']
        if source=='pasqal_cloud_retry':
            candidates=[r for r in retries if r['canonical_id']==row['id'] and Path(r['source_prepared_root']).resolve()==(ROOT/('transferred_prepared' if transfer else 'prepared')).resolve()]
            assert len(candidates)==1
            return Path(candidates[0]['retry_output_root'])/candidates[0]['retry_id']
        raise ValueError('Unknown canonical source '+str(source))
    checked=[];failures=[];cache={};unique_shots=0
    for row in rows:
        if row['status']!='completed':continue
        try:
            folder=locate(row);state=read(folder/'state.json');assert state['status']=='completed'
            key=(str(folder.resolve()),row['tier'],int(row['instance_seed']),row['encoding'])
            if key not in cache:
                raw=read(folder/'counts.json');result=evaluate(raw,state['result_atom_order'],instances[(row['tier'],int(row['instance_seed']))],row['encoding'])
                assert result['shots']==2000
                if state.get('shots') is not None:assert state['shots']==result['shots']
                cache[key]=result;unique_shots+=result['shots']
            result=cache[key];comparisons=[]
            for field in ['shots','valid_code_count','feasible_count','optimal_clustering_count','valid_code_rate','feasibility_rate','optimal_clustering_rate','best_feasible_f','model_gap_pct','optimal_cvrp_count','optimal_cvrp_rate','best_feasible_cvrp','cvrp_gap_pct','selected_clustering_f','best_clustering_cvrp','best_clustering_cvrp_gap_pct']+(['slack_exact_count','slack_exact_rate'] if row['encoding']=='slack' else []):
                a=result[field];b=number(row.get(field));assert (a is None)==(b is None),(field,a,b)
                if a is not None:assert abs(a-b)<=TOL,(field,a,b)
                comparisons.append(field)
            stored_assignment=row.get('best_assignment');stored_assignment=json.loads(stored_assignment) if stored_assignment and stored_assignment not in ('nan','None') else None
            assert result['best_assignment']==stored_assignment,('best_assignment',result['best_assignment'],stored_assignment)
            comparisons.append('best_assignment')
            checked.append(dict(id=row['id'],cohort=row['cohort'],source=row['result_source'],raw_folder=str(folder),
                counts_sha256=digest(folder/'counts.json'),state_sha256=digest(folder/'state.json'),
                result_atom_order=state['result_atom_order'],metrics_checked=comparisons,independent_result=result))
        except Exception as e:failures.append(dict(id=row['id'],error=repr(e)))
    if any(digest(Path(p))!=h for p,h in ledger_hashes.items()):failures.append(dict(error='Canonical CSV snapshot changed during verification; rerun against stable snapshot'))
    output=dict(status='passed' if not failures else 'failed',snapshot_verified_at=datetime.now(ZoneInfo('America/New_York')).isoformat(),
        ledger_sha256=ledger_hashes,verifier_sha256=digest(Path(__file__)),reference_sha256=digest(ROOT/'references/instances.json'),
        completed_ledger_references=sum(r['status']=='completed' for r in rows),verified_references=len(checked),unique_raw_sources=len(cache),unique_raw_measurements=unique_shots,
        primary_conditions_verified=sum(r['cohort']=='primary' for r in checked),transferred_conditions_verified=sum(r['cohort']=='transferred_penalties' for r in checked),
        accuracy_references_verified=sum(r['cohort'] in ['accuracy','transferred_accuracy'] for r in checked),
        failures=failures,seconds=time.perf_counter()-started,
        limitations=['Snapshot only; rerun after analyzer refresh to cover new completed results.','Routing scoring independently checked using stored exact per-subset tour costs; those tour optimality proofs are reused, not re-proven here.','Exact clustering reference values are reused, not independently proven here.','Physical embedding fidelity and simulator accuracy are outside scope.'],checks=checked)
    (ROOT/'observed_counts_verification.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='checks'},indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':run()
