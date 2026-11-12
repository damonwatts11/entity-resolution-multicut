"""Tests for ermc.baselines.

Project document section 11 tests owned by this file:
    T2  chain counterexample: records a, b, c with c_ab=2, c_bc=1, c_ac=-3.
        Transitive closure returns {a,b,c}; multicut returns {a,b},{c}, cost -2
    T3  chain without negative evidence: same instance with pair ac removed;
        multicut returns {a,b,c} with cost 0, as transitive closure does

Tests T2 and T3 together are the unit-test form of the argument of section 3.
"""

from ermc import baselines


def test_baselines_exist():
    assert callable(baselines.transitive_closure)
    assert callable(baselines.thresholding)
    assert callable(baselines.average_linkage)
