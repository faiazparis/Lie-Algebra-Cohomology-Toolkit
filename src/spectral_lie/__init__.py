"""
Lie Algebra Cohomology Toolkit

A mathematically rigorous implementation of Lie algebra cohomology
using Chevalley-Eilenberg differentials and Hodge theory for spectral analysis.

CAPABILITIES:
✅ Core cohomology computation (always works)
✅ Spectral analysis of Hodge Laplacian
✅ JSON structure constants input (reliable)
⚠️  SageMath integration (experimental, optional)

RECOMMENDATION: Use JSON input for production work.
               SageMath integration is best for academic research.

For detailed usage and limitations, see README.md and BUILT_AND_ROADMAP.md
"""

__version__ = "1.0.0"
__author__ = "Lie Algebra Cohomology Toolkit Team"

from .registry import REGISTRY, register, get_component

__all__ = ["REGISTRY", "register", "get_component"]
