"""Tests for ermc.kernels.

Project document section 11 tests owned by this file:
    T8   proposition 3 (property, random regions, difference equals Delta)
    T9   kernel formation: sizes at most B, Delta equals abandoned positive cost
    T10  kernel formation, no cap: kernels equal components of G+, Delta = 0
"""

from ermc import kernels


def test_form_kernels_exists():
    assert callable(kernels.form_kernels)
