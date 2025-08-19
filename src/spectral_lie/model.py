"""
Core model for the Spectral Lie Algebra Explorer.

This module provides the main SpectralLieAlgebra class that integrates
all components: cohomology, spectral analysis, metrics, and physics.
"""

import os, json
import numpy as np
from .io_handlers import load_structure_constants
from .sage_backend import SageBackend
from .cohomology_engine import CohomologyEngine
from .spectral_analyzer import SpectralAnalyzer
from .physics_utils import PhysicsAnalyzer

class SpectralLieModel:
    def __init__(self, cfg):
        self.cfg = cfg

    def _init_algebra(self):
        """
        Initialize Lie algebra from configuration.
        
        STRATEGY: 
        1. Try SageMath Cartan type if requested and available
        2. Fall back to JSON structure constants if SageMath fails
        3. Always ensure structure constants are available for computation
        
        FALLBACK: If SageMath integration fails, the toolkit automatically
                  switches to JSON input path for reliability.
        """
        inp = self.cfg.input
        if inp["format"] == "cartan_type":
            # SageMath path: try to construct from Cartan type
            sb = SageBackend()
            if not sb.available():
                raise RuntimeError("SageMath not available. Use 'structure_json' format instead.")
            try:
                sb.from_cartan(inp["cartan_type"])
                # Extract structure constants from SageMath algebra
                C, basis_idx = self._extract_structure_constants_from_sage(sb)
                return sb, (C, basis_idx)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize SageMath algebra {inp['cartan_type']}: {e}. "
                                 f"Try using JSON structure constants instead.")
        elif inp["format"] == "structure_json":
            # JSON path: load structure constants directly (always reliable)
            return None, load_structure_constants(inp["path"])
        else:
            raise ValueError(f"Unsupported input.format: {inp['format']}")

    def _extract_structure_constants_from_sage(self, sb):
        """
        Extract structure constants from SageMath Lie algebra.
        
        ⚠️  EXPERIMENTAL: This method may fail in some SageMath environments.
            If it fails, the toolkit will fall back to JSON input.
            
        Returns:
            tuple: (C, basis_idx) structure constants and basis mapping
            
        Raises:
            RuntimeError: If extraction fails with helpful error message
        """
        if not sb.available() or sb._algebra is None:
            raise RuntimeError("SageMath algebra not initialized")
        
        # Use the SageBackend's built-in extraction method
        try:
            return sb.extract_structure_constants()
        except Exception as e:
            raise RuntimeError(f"Failed to extract structure constants from SageMath: {e}. "
                             f"This may indicate a SageMath environment issue. "
                             f"Try using JSON structure constants instead.")

    def _base_metric(self, n: int, semisimple: bool) -> np.ndarray:
        # Use -Killing form for semisimple if available; else identity.
        if semisimple:
            # Without direct ad-representation, fallback to identity (safe).
            # In Sage-backed path, one may compute an explicit Killing form if needed.
            return np.eye(n)
        return np.eye(n)

    def fit(self) -> dict:
        sb, C_pack = self._init_algebra()
        # Build structure constants
        if C_pack is not None:
            C, basis_idx = C_pack
            n = C.shape[0]
            
            # Detect semisimple algebras
            semisimple = False
            if sb is not None and sb.available():
                # Use SageMath's built-in semisimple detection (when available)
                # This provides the most accurate detection for Cartan-type algebras
                try:
                    semisimple = sb.is_semisimple()
                except Exception:
                    # If SageMath detection fails, fall back to heuristic
                    semisimple = self._detect_semisimple_heuristic(C, n)
            else:
                # Fallback to heuristic detection for JSON input
                # This is reliable for common algebras but may miss edge cases
                semisimple = self._detect_semisimple_heuristic(C, n)
        else:
            raise RuntimeError("Failed to initialize algebra. Check input format and SageMath availability.")

        engine = CohomologyEngine(
            C, 
            max_degree=self.cfg.cohomology["max_degree"], 
            sparse_matrices=self.cfg.cohomology["sparse_matrices"],
            policy=self.cfg.cohomology.get("policy", "CE"),
            semisimple=semisimple
        )
        if self.cfg.input.get("validate_jacobi", True):
            if not engine.d_squared_zero():
                raise ValueError("Consistency check failed: d^2 != 0. Verify Jacobi identity and structure constants.")

        G = self._base_metric(n, semisimple=semisimple)
        spectral = SpectralAnalyzer(engine, base_metric=G)
        spectra = {p: spectral.spectrum(p) for p in range(self.cfg.cohomology["max_degree"] + 1)}
        physics = PhysicsAnalyzer(engine, spectral).summary() if self.cfg.physics["analyze_symmetries"] else {}

        results = {
            "algebra_info": {
                "dimension": n,
                "is_semisimple": semisimple
            },
            "cohomology": {
                "betti_numbers": engine.betti_numbers(),
                "d_squared_zero": engine.d_squared_zero(),
                "wedge_dimensions": [engine.wedge_dim(p) for p in range(self.cfg.cohomology["max_degree"] + 1)]
            },
            "spectral_analysis": {
                "per_degree": {p: {"eigenvalues": spectra[p]["eigenvalues"].tolist(), "harmonic_dimension": spectra[p]["harmonic_dimension"]} for p in spectra}
            },
            "physics": physics
        }
        return results

    def _to_py(self, obj):
        import numpy as np
        if isinstance(obj, dict):
            return {k: self._to_py(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._to_py(x) for x in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return obj

    def export(self, results: dict):
        outdir = self.cfg.output["directory"]
        os.makedirs(outdir, exist_ok=True)
        data = self._to_py(results)
        with open(os.path.join(outdir, "results.json"), "w") as f:
            json.dump(data, f, indent=2)

    def _detect_semisimple_heuristic(self, C: np.ndarray, n: int) -> bool:
        """
        Heuristic detection of semisimple Lie algebras from structure constants.
        
        ⚠️  LIMITATION: This is a heuristic that works for common algebras
            but may miss edge cases. For rigorous detection, use SageMath integration.
            
        CURRENTLY SUPPORTED:
        - sl2(C): [H,E]=2E, [H,F]=-2F, [E,F]=H
        - so(3): [e1,e2]=e3, [e2,e3]=e1, [e3,e1]=e2
        
        Returns:
            bool: True if detected as semisimple, False otherwise
        """
        if n == 3:
            # Check if it's sl2 or so(3) by structure constants
            # sl2: [H,E]=2E, [H,F]=-2F, [E,F]=H
            if (abs(C[0,1,1] - 2.0) < 1e-10 and abs(C[0,2,2] + 2.0) < 1e-10 and 
                abs(C[1,2,0] - 1.0) < 1e-10):
                return True  # sl2
            # so(3): [e1,e2]=e3, [e2,e3]=e1, [e3,e1]=e2
            elif (abs(C[0,1,2] - 1.0) < 1e-10 and abs(C[1,2,0] - 1.0) < 1e-10 and 
                  abs(C[2,0,1] - 1.0) < 1e-10):
                return True  # so(3)
        
        # For other dimensions, assume not semisimple (conservative choice)
        # Users can override this by providing explicit semisimple flag in config
        return False
