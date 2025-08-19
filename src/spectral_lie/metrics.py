"""
Metric tensors and induced inner products for Hodge theory.

This module implements induced inner products on exterior powers Alt^p(g*)
and provides the foundation for Hodge Laplacian construction.
"""

import numpy as np
from itertools import combinations

def induced_metric(G: np.ndarray, p: int) -> np.ndarray:
    """
    Induced inner product on Alt^p(g*):
    <e_I, e_J> = det(G[I,J]) for multi-indices I,J.
    """
    n = G.shape[0]
    if p == 0:
        return np.array([[1.0]])
    if p < 0 or p > n:
        return np.zeros((0, 0))
    basis = list(combinations(range(n), p))
    m = len(basis)
    Gram = np.zeros((m, m), dtype=float)
    for a, I in enumerate(basis):
        for b, J in enumerate(basis):
            Gram[a, b] = np.linalg.det(G[np.ix_(I, J)])
    # Symmetrize numerically
    return 0.5 * (Gram + Gram.T)
