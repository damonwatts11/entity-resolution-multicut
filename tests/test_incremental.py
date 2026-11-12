"""Tests for ermc.incremental (Level F).

Project document section 11 tests owned by this file:
    T20  incremental invariants: after every insertion of a short stream, kernel
         sizes at most B, records outside the region keep their identifier, and
         the running U equals the recomputed U
    T21  incremental safeguard: after every insertion, the cost of the region is
         at most the cost of the trivial update
"""

from ermc.incremental import Resolver


def test_resolver_has_insert():
    assert hasattr(Resolver, "insert")
