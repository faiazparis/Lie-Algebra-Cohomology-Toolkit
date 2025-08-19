"""
Spectral analyzer for the Hodge Laplacian.

This module implements the Hodge Laplacian operator Δp = dp*dp + dp−1dp−1*
and provides spectral analysis tools for Lie algebra cohomology.
"""

import numpy as np
import scipy.linalg as la
from .metrics import induced_metric

class SpectralAnalyzer:
    def __init__(self, engine, base_metric: np.ndarray):
        self.engine = engine
        self.G = base_metric

    def laplacian(self, p: int) -> np.ndarray:
        # Metrics
        Gp   = induced_metric(self.G, p)
        Gp1  = induced_metric(self.G, p + 1)
        Gpm1 = induced_metric(self.G, p - 1)
        d_p  = self.engine.assemble_d(p)        # C^p -> C^{p+1}
        d_m1 = self.engine.assemble_d(p - 1)    # C^{p-1} -> C^{p}

        # Handle empty spaces
        if Gp.size == 0:
            return np.zeros((0, 0))

        L = np.zeros(Gp.shape)
        if d_p.size and Gp1.size and Gp.size > 0:
            Gp_inv = np.linalg.pinv(Gp)
            d_star = Gp_inv @ d_p.T @ Gp1
            L += d_star @ d_p
        if d_m1.size and Gpm1.size and Gpm1.size > 0:
            Gpm1_inv = np.linalg.pinv(Gpm1)
            d_m1_star = Gpm1_inv @ d_m1.T @ Gp
            L += d_m1 @ d_m1_star
        # Hermitian symmetrization
        L = 0.5 * (L + L.T)
        return L

    def spectrum(self, p: int) -> dict:
        L = self.laplacian(p)
        if L.size == 0:
            return {"eigenvalues": np.array([]), "harmonic_dimension": 0}
        w, _ = la.eigh(L)
        tol = 1e-10
        harm = int(np.sum(np.abs(w) < tol))
        return {"eigenvalues": w, "harmonic_dimension": harm}
