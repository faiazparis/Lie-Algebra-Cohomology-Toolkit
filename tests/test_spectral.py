"""
Tests for spectral analyzer and Hodge Laplacian computation.
"""

import numpy as np
from spectral_lie.cohomology_engine import CohomologyEngine
from spectral_lie.spectral_analyzer import SpectralAnalyzer

def test_laplacian_psd():
    n = 3
    C = np.zeros((n,n,n))
    engine = CohomologyEngine(C, max_degree=1, sparse_matrices=False)
    G = np.eye(n)
    spec = SpectralAnalyzer(engine, base_metric=G)
    L0 = spec.laplacian(0)
    w, _ = np.linalg.eigh(0.5*(L0+L0.T))
    assert (w >= -1e-10).all()
