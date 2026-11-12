"""Tests for ermc.bounds.

Project document section 11 tests owned by this file:
    T12  order of bounds (property): L_0 <= L_pack <= OPT <= cost after local
         search <= cost after greedy contraction
"""

from ermc import bounds


def test_bounds_exist():
    assert callable(bounds.trivial_bound)
    assert callable(bounds.cycle_packing_bound)
    assert callable(bounds.lower_bound)
