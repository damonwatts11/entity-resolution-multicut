"""Tests for ermc.persistency.

Project document section 11 tests owned by this file:
    T5  persistency preserves the optimum (property, >=500 instances, brute ref)
    T6  proposition 2 hand case: vertex with incident costs 5, -2, 1
    T7  contraction preserves partition cost
"""

from ermc import persistency


def test_reduce_exists():
    assert callable(persistency.reduce)
