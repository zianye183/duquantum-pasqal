import itertools
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from references import evaluate, make_candidate, partition_dp, TOL, make_instance, score_counts, slack_weights, first_feasible_packing

class ExactReferenceTests(unittest.TestCase):
    def test_randomized_direct_assignments_and_tours(self):
        for seed in range(12):
            rng=np.random.default_rng(seed)
            n=3+seed%4; k=1+seed%3; cap=3+seed%5
            xy=rng.uniform(0,10,(n,2)); demands=rng.integers(1,4,n)
            depot=np.array([5,5]); costs=[]; partitions=set(); best=float('inf'); routed=float('inf')
            dist=np.linalg.norm(xy[:,None]-xy[None,:],axis=-1)
            for assignment in itertools.product(range(k),repeat=n):
                groups=tuple(sorted(tuple(i for i in range(n) if assignment[i]==label) for label in range(k) if label in assignment))
                if groups in partitions: continue
                partitions.add(groups)
                if any(sum(demands[i] for i in group)>cap for group in groups): continue
                cluster=sum(dist[i,j] for group in groups for i,j in itertools.combinations(group,2))
                costs.append(cluster); best=min(best,cluster)
                route=0
                for group in groups:
                    route+=min(np.linalg.norm(np.diff(np.vstack([depot,xy[list(order)],depot]),axis=0),axis=1).sum()
                               for order in itertools.permutations(group))
                routed=min(routed,route)
            rec=evaluate(dict(seed=seed,tier='test',coordinates=xy.tolist(),demands=demands.tolist(),capacity=cap,vehicles=k,depot=depot.tolist()))
            self.assertEqual(rec['feasible'],bool(costs))
            if costs:
                self.assertAlmostEqual(rec['model_reference'],best,places=7)
                self.assertAlmostEqual(rec['cvrp_reference'],routed,places=7)
                self.assertEqual(rec['distinct_model_optima'],sum(abs(c-best)<=1e-8 for c in costs))
                cert=rec['certificate']
                self.assertEqual(len(cert),n)
                self.assertTrue(all(sum(demands[i] for i in range(n) if cert[i]==label)<=cap for label in range(k)))

    def test_unlabeled_ties_unused_vehicles_and_infeasibility(self):
        rec=evaluate(dict(coordinates=[[0,0]]*4,demands=[1]*4,capacity=4,vehicles=3,depot=[0,0]))
        # Stirling S(4,1)+S(4,2)+S(4,3) = 1+7+6.
        self.assertEqual(rec['distinct_model_optima'],14)
        self.assertEqual(rec['cvrp_reference'],0.)
        bad=evaluate(dict(coordinates=[[0,0]]*3,demands=[2]*3,capacity=3,vehicles=2,depot=[0,0]))
        self.assertFalse(bad['feasible'])  # Total-demand bound alone passes.

    def test_tie_tolerance_is_global_not_per_group(self):
        rng=np.random.default_rng(91); n=5; k=3
        loads=np.array([mask.bit_count() for mask in range(1<<n)])
        costs=rng.uniform(0,2*TOL,1<<n); costs[0]=0
        partitions=set()
        for assignment in itertools.product(range(k),repeat=n):
            groups=tuple(sorted(sum(1<<i for i in range(n) if assignment[i]==label) for label in range(k) if label in assignment))
            partitions.add(groups)
        values=[sum(costs[mask] for mask in groups) for groups in partitions]
        expected=min(values)
        result=partition_dp(loads,costs,n,k)
        self.assertAlmostEqual(result['objective'],expected,places=15)
        self.assertEqual(result['distinct_optima'],sum(v<=expected+TOL for v in values))

    def test_seed_generation_preserves_first_draw(self):
        for tier,seed,n,top in [('M',7000,10,8),('L',8000,15,10)]:
            rec=make_candidate(tier,seed); rng=np.random.default_rng(seed)
            self.assertEqual(rec['coordinates'],rng.uniform(0,100,(n,2)).tolist())
            self.assertEqual(rec['demands'],rng.integers(1,top+1,n).tolist())

    def test_known_medium_large_cases(self):
        import json
        for old in json.loads(Path(__file__).with_name('known_cases.json').read_text()):
            new=evaluate(old)
            self.assertAlmostEqual(old['model_reference'],new['model_reference'],places=8)
            self.assertAlmostEqual(old['cvrp_reference'],new['cvrp_reference'],places=8)
            self.assertEqual(old['distinct_model_optima'],new['distinct_model_optima'])

    def test_scoring_encoding_slack_and_invalid_bits(self):
        inst=make_instance('S',2002); n,k=inst['N'],inst['K']; assign=inst['certificate']
        reduced=''.join(str(int(a==j)) for a in assign for j in range(1,k))
        result=score_counts({reduced:10},inst,'reduced')
        self.assertEqual(result['optimal_clustering_rate'],1)
        self.assertEqual(result['model_gap_pct'],0)
        x=''.join(str(int(a==j)) for j in range(k) for a in assign)
        weights=slack_weights(inst['Q']); sbits=''
        for j in range(k):
            slack=inst['Q']-sum(q for q,a in zip(inst['q'],assign) if a==j)
            sbits+=''.join(map(str,next(b for b in itertools.product((0,1),repeat=len(weights)) if sum(i*w for i,w in zip(b,weights))==slack)))
        result=score_counts({x+sbits:8,'0'*len(x+sbits):2},inst,'slack')
        self.assertEqual(result['feasibility_rate'],.8)
        self.assertEqual(result['optimal_clustering_rate'],.8)
        self.assertEqual(result['slack_exact_rate'],.8)
        # Wrong auxiliary bits do not invalidate a valid clustering.
        result=score_counts({x+'0'*len(sbits):10},inst,'slack')
        self.assertEqual(result['feasibility_rate'],1)
        self.assertEqual(result['slack_exact_rate'],0)
        with self.assertRaises(ValueError): score_counts({'1':1},inst)
        with self.assertRaises(ValueError): score_counts({reduced:-1},inst)

    def test_feasible_certificate_uses_only_demands(self):
        for q,k,cap in [([4,4,3,3],2,7),([2,2,2],2,3),([3,2,2,1],3,4)]:
            expected=next((list(a) for a in itertools.product(range(k),repeat=len(q))
                if all(sum(v for v,g in zip(q,a) if g==label)<=cap for label in range(k))),None)
            self.assertEqual(first_feasible_packing(q,k,cap),expected)

    def test_route_of_best_clustering_is_distinct_and_stable(self):
        inst=make_instance('S',2002)
        counts={''.join(map(str,a)):1 for a in itertools.product((0,1),repeat=4)}
        forward=score_counts(counts,inst)
        reverse=score_counts(dict(reversed(list(counts.items()))),inst)
        self.assertEqual(forward,reverse)
        self.assertEqual(forward['model_gap_pct'],0)
        self.assertEqual(forward['cvrp_gap_pct'],0)
        assignment=forward['best_assignment']
        masks=[sum(1<<i for i,a in enumerate(assignment) if a==k) for k in range(inst['K'])]
        self.assertEqual(forward['best_clustering_cvrp'],sum(inst['tour_costs'][m] for m in masks))
        self.assertGreaterEqual(forward['best_clustering_cvrp'],forward['best_feasible_cvrp'])
        self.assertIsNone(score_counts({next(iter(counts)):0},inst)['best_clustering_cvrp'])

if __name__=='__main__': unittest.main()
