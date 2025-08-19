"""
Tests for Chevalley-Eilenberg cohomology engine.
"""

import numpy as np
from spectral_lie.cohomology_engine import CohomologyEngine

def test_d_squared_zero_sl2():
    # sl2 structure constants:
    # [H,E]=2E, [H,F]=-2F, [E,F]=H
    basis = ["H","E","F"]
    idx = {b:i for i,b in enumerate(basis)}
    n = 3
    C = np.zeros((n,n,n), dtype=float)
    def setc(a,b,c,val):
        ia, ib, ic = idx[a], idx[b], idx[c]
        C[ia, ib, ic] += val
        C[ib, ia, ic] -= val
    setc("H","E","E", 2.0)
    setc("H","F","F",-2.0)
    setc("E","F","H", 1.0)

    engine = CohomologyEngine(C, max_degree=2, sparse_matrices=False)
    assert engine.d_squared_zero()
