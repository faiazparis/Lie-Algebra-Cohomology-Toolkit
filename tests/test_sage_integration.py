"""
Tests for SageMath integration and backend functionality.
"""

import pytest
from spectral_lie.sage_backend import SageBackend

def test_sage_available_or_skip():
    sb = SageBackend()
    if not sb.available():
        pytest.skip("SageMath not available")
    sb.from_cartan("A1")
    assert sb.verify_jacobi()
    assert sb.is_semisimple()
    assert sb.dimension() > 0
