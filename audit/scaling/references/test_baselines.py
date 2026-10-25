import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from baselines import random_assignments,greedy_demand_first,reduced_bits

class BaselineTests(unittest.TestCase):
    def test_balanced_cardinality(self):
        for n,k in [(4,2),(10,3),(15,4)]:
            values=random_assignments(n,k,2000,0,'balanced_cardinality')
            self.assertEqual(values.shape,(2000,n))
            for row in values:
                counts=np.bincount(row,minlength=k)
                self.assertLessEqual(int(counts.max()-counts.min()),1)
                self.assertEqual(len(reduced_bits(row,k)),n*(k-1))
    def test_seed_repeatability(self):
        for method in ('uniform_assignment','balanced_cardinality'):
            a=random_assignments(10,3,2000,0,method)
            np.testing.assert_array_equal(a,random_assignments(10,3,2000,0,method))
            self.assertFalse(np.array_equal(a,random_assignments(10,3,2000,1,method)))
    def test_greedy_validates_capacity(self):
        q=[4,4,3,3];a=greedy_demand_first(q,2,7)
        self.assertEqual(a,[0,1,0,1])
        self.assertTrue(all(sum(v for v,g in zip(q,a) if g==k)<=7 for k in range(2)))
        self.assertIsNone(greedy_demand_first([2,2,2],2,3))

if __name__=='__main__':unittest.main()
