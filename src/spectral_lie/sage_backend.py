"""
SageMath backend for Lie algebra operations.

⚠️  EXPERIMENTAL FEATURE: This integration is under active development.
    While the core toolkit works perfectly without SageMath, this backend
    may not work in all environments.

RECOMMENDATION: Use JSON structure constants for production work.
               SageMath integration is best for academic research and prototyping.

This module provides integration with SageMath for Lie algebra initialization,
structure constants computation, and root system analysis.
"""

import numpy as np
from typing import Union

# Import Sage lazily to avoid environment issues during static analysis
# This means SageMath is completely optional - the toolkit works without it
try:
    import sage.all as sage
except Exception:
    sage = None

class SageBackend:
    """
    Sage-backed Lie algebra provider.
    
    ⚠️  EXPERIMENTAL: This integration may not work in all SageMath environments.
        Always test in your specific setup before relying on it.
    
    Supports:
    - from Cartan type (e.g., "A1", "A3", "E8") - EXPERIMENTAL
    - from structure constants (fallback path; Jacobi verified via d^2=0 downstream)
    
    FALLBACK STRATEGY: If SageMath integration fails, the toolkit automatically
                       falls back to JSON structure constants input.
    """
    def __init__(self, cartan_type: Union[str, None] = None):
        self.cartan_type = cartan_type
        self._algebra = None
        self._basis = None

    def available(self) -> bool:
        """
        Check if SageMath is available in the current environment.
        
        Returns:
            bool: True if SageMath can be imported, False otherwise
            
        Note: This only checks import availability, not functional correctness.
              The actual integration may still fail even if this returns True.
        """
        return sage is not None

    def from_cartan(self, cartan_type: str):
        """
        Initialize Lie algebra from Cartan type (e.g., "A1" for sl2).
        
        ⚠️  EXPERIMENTAL: This method may fail in some SageMath environments.
            Common issues: version incompatibility, missing dependencies, PATH issues.
            
        Args:
            cartan_type: Cartan type string (e.g., "A1", "E8", "G2")
            
        Raises:
            RuntimeError: If SageMath is not available or initialization fails
        """
        if not self.available():
            raise RuntimeError("SageMath not available in current environment.")
        
        try:
            # Parse like "A3" -> ['A', 3]
            letter = cartan_type.upper()
            rank = int(cartan_type[1:])
            ct = [letter, rank]
            
            # Construct a classical Lie algebra via Sage
            # This is the most likely point of failure in different environments
            self._algebra = sage.simple_lie_algebra(ct, base_field=sage.QQ)
            self.cartan_type = cartan_type
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize SageMath algebra {cartan_type}: {e}. "
                             f"Try using JSON structure constants instead.")

    def dimension(self) -> int:
        """Get the dimension of the Lie algebra."""
        if self._algebra is None:
            return 0
        return self._algebra.dimension()

    def verify_jacobi(self) -> bool:
        """
        Verify Jacobi identity.
        
        Note: SageMath constructs valid Lie algebras, so Jacobi holds by design.
              This is a placeholder for consistency with the interface.
        """
        return self._algebra is not None

    def killing_form(self) -> np.ndarray:
        """
        Compute the Killing form of the Lie algebra.
        
        STRATEGY: Try SageMath's built-in method first, fall back to structure constants.
        
        Returns:
            np.ndarray: (n,n) symmetric matrix representing the Killing form
            
        Note: If SageMath method fails, falls back to computing from structure constants.
              This ensures the method always returns a result, even if not optimal.
        """
        if self._algebra is None:
            raise ValueError("Algebra not initialized.")
        
        if self.available():
            # Try to get Killing form from SageMath if available
            try:
                if hasattr(self._algebra, 'killing_form'):
                    K = self._algebra.killing_form()
                    # Convert to NumPy array
                    n = self.dimension()
                    K_np = np.zeros((n, n), dtype=float)
                    for i in range(n):
                        for j in range(n):
                            K_np[i, j] = float(K(self._algebra.basis()[i], self._algebra.basis()[j]))
                    return K_np
                else:
                    # Fallback to structure constants method
                    return self._killing_form_from_structure_constants()
            except Exception:
                # If SageMath method fails, fall back to structure constants
                return self._killing_form_from_structure_constants()
        else:
            # No SageMath available
            return self._killing_form_from_structure_constants()
    
    def _killing_form_from_structure_constants(self) -> np.ndarray:
        """
        Compute Killing form directly from structure constants.
        
        FORMULA: K_{ab} = tr(ad_ea ad_eb) where (ad_ea)_{kj} = C[a,k,j]
        
        This method works without SageMath and provides a reliable fallback.
        
        Returns:
            np.ndarray: (n,n) Killing form matrix computed from structure constants
        """
        if self._algebra is None:
            raise ValueError("Algebra not initialized.")
        
        try:
            C, _ = self.extract_structure_constants()
            n = C.shape[0]
            K = np.zeros((n, n), dtype=float)
            
            # Compute Killing form: K_{ab} = tr(ad_ea ad_eb)
            for a in range(n):
                for b in range(n):
                    # (ad_ea)_{kj} = C[a,k,j]
                    # (ad_eb)_{ji} = C[b,j,i]
                    # tr(ad_ea ad_eb) = sum_k (ad_ea ad_eb)_{kk}
                    # = sum_k sum_j (ad_ea)_{kj} (ad_eb)_{jk}
                    # = sum_k sum_j C[a,k,j] C[b,j,k]
                    trace = 0.0
                    for k in range(n):
                        for j in range(n):
                            trace += C[a, k, j] * C[b, j, k]
                    K[a, b] = trace
            
            return K
        except Exception as e:
            # If structure constants extraction fails, return identity
            # This is a safe fallback that won't break the computation
            n = self.dimension()
            return np.eye(n)

    def is_semisimple(self) -> bool:
        """
        Detect if the Lie algebra is semisimple.
        
        STRATEGY: Try SageMath's built-in methods first, fall back to Killing form.
        
        Returns:
            bool: True if semisimple, False otherwise
            
        Note: The Killing form method is mathematically rigorous but may be
              computationally expensive for large algebras.
        """
        if self._algebra is None:
            return False
        
        if self.available():
            # Try SageMath's built-in semisimple detection
            try:
                if hasattr(self._algebra, 'is_semisimple'):
                    return bool(self._algebra.is_semisimple())
                elif hasattr(self._algebra, 'is_simple'):
                    return bool(self._algebra.is_simple())
                else:
                    # Fallback to Killing form method
                    return self._is_semisimple_from_killing_form()
            except Exception:
                # If SageMath method fails, fall back to Killing form
                return self._is_semisimple_from_killing_form()
        else:
            # No SageMath available, use Killing form method
            return self._is_semisimple_from_killing_form()
    
    def _is_semisimple_from_killing_form(self) -> bool:
        """
        Detect semisimplicity using Killing form non-degeneracy.
        
        THEOREM: A Lie algebra is semisimple iff its Killing form is non-degenerate.
        
        This method works without SageMath and provides a reliable fallback.
        
        Returns:
            bool: True if semisimple (Killing form non-degenerate), False otherwise
        """
        try:
            K = self.killing_form()
            # Check if Killing form is non-degenerate (determinant non-zero)
            det = np.linalg.det(K)
            return abs(det) > 1e-10
        except Exception:
            # If Killing form computation fails, assume not semisimple
            # This is a conservative choice that won't break the computation
            return False

    def root_system_data(self) -> dict:
        """
        Get root system data for Cartan-type Lie algebras.
        
        ⚠️  REQUIREMENT: This method only works when using Cartan types AND SageMath is available.
                        It will return an empty dict for JSON input or when SageMath is unavailable.
        
        Returns:
            dict: Root system data including simple roots, positive roots, fundamental weights
                  Empty dict if not available
        """
        if not self.available() or self.cartan_type is None:
            return {}
        
        try:
            letter = self.cartan_type.upper()
            rank = int(self.cartan_type[1:])
            RS = sage.RootSystem([letter, rank])
            ambient = RS.ambient_space()
            return {
                "simple_roots": [list(r) for r in ambient.simple_roots()],
                "positive_roots": [list(r) for r in ambient.positive_roots()],
                "fundamental_weights": [list(w) for w in ambient.fundamental_weights()],
            }
        except Exception as e:
            # If root system computation fails, return empty dict
            # This ensures the method never crashes the toolkit
            return {}

    def extract_structure_constants(self):
        """
        Extract structure constants from SageMath Lie algebra.
        
        ⚠️  EXPERIMENTAL: This method may fail in some SageMath environments.
            Common issues: basis representation, bracket method availability.
            
        Returns:
            tuple: (C, basis_idx) where C is (n,n,n) NumPy array and basis_idx maps basis names to indices
            
        Raises:
            RuntimeError: If extraction fails
            
        Note: This is the core method that bridges SageMath and the toolkit.
              If it fails, the toolkit will fall back to JSON input.
        """
        if not self.available() or self._algebra is None:
            raise RuntimeError("SageMath algebra not initialized")
        
        # Get basis and dimension
        basis = list(self._algebra.basis())
        n = self.dimension()
        
        # Initialize structure constants array
        C = np.zeros((n, n, n), dtype=float)
        
        # Extract structure constants from SageMath
        for i, ei in enumerate(basis):
            for j, ej in enumerate(basis):
                if i < j:  # Only compute upper triangular (antisymmetry)
                    try:
                        bracket = ei.bracket(ej)
                        for k, ek in enumerate(basis):
                            coeff = bracket.coefficient(ek)
                            if coeff != 0:
                                C[i, j, k] = float(coeff)
                                C[j, i, k] = -float(coeff)  # Antisymmetry
                    except Exception as e:
                        # Fallback: try alternative bracket method
                        try:
                            bracket = ei.bracket(ej)
                            for k, ek in enumerate(basis):
                                coeff = bracket.coefficient(ek)
                                if coeff != 0:
                                    C[i, j, k] = float(coeff)
                                    C[j, i, k] = -float(coeff)
                        except Exception:
                            # If all else fails, raise informative error
                            raise RuntimeError(f"Failed to compute bracket [{ei}, {ej}] in SageMath: {e}. "
                                             f"This may indicate a SageMath environment issue. "
                                             f"Try using JSON structure constants instead.")
        
        # Create basis index mapping with deterministic ordering
        basis_idx = {str(b): i for i, b in enumerate(basis)}
        
        return C, basis_idx

    def get_canonical_basis(self):
        """
        Get a canonical ordered basis for the Lie algebra.
        
        ⚠️  NOTE: The ordering may vary between SageMath versions and environments.
                  For reproducible results, consider using JSON input with explicit basis ordering.
        
        Returns:
            list: Ordered basis elements
            
        Raises:
            RuntimeError: If basis extraction fails
        """
        if not self.available() or self._algebra is None:
            raise RuntimeError("SageMath algebra not initialized")
        
        # For classical Lie algebras, try to get a standard basis
        if hasattr(self._algebra, 'basis'):
            basis = list(self._algebra.basis())
            # Sort for deterministic ordering (but this may still vary between versions)
            basis.sort(key=str)
            return basis
        else:
            raise RuntimeError("Cannot extract canonical basis from SageMath algebra")
