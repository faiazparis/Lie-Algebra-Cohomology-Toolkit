"""
Input/Output handlers for the Spectral Lie Algebra Explorer.

This module provides utilities for reading, writing, and serializing
Lie algebra data, configuration files, and analysis results.
"""

import json
import numpy as np

def load_structure_constants(path: str):
    """
    JSON schema:
    {
      "basis": ["H","E","F"],
      "structure_constants": [
        [["H","E"], {"E": 2}],
        [["H","F"], {"F": -2}],
        [["E","F"], {"H": 1}]
      ]
    }
    Returns:
      C: (n,n,n) with C[i,j,k] = c^k_{ij}, antisymmetrized.
      basis_index: dict name->idx
    """
    with open(path, "r") as f:
        obj = json.load(f)
    basis = obj["basis"]
    idx = {b: i for i, b in enumerate(basis)}
    n = len(basis)
    C = np.zeros((n, n, n), dtype=float)
    for pair, lincomb in obj["structure_constants"]:
        i, j = idx[pair[0]], idx[pair[1]]
        for name_k, val in lincomb.items():
            k = idx[name_k]
            C[i, j, k] += float(val)
            C[j, i, k] -= float(val)  # antisymmetry
    return C, idx
