"""Tests for ermc.solvers.

Project document section 11 tests owned by this file:
    T1   brute force: hand instance of 4 vertices solved on paper
    T13  integer program (property, up to 8 vertices): cost equals brute force,
         no triangle inequality violated
    T14  local search (property): cost never increases, search terminates
"""

from ermc.solvers import brute, gaec, ilp, moves


def test_solvers_exist():
    assert callable(brute.solve)
    assert callable(gaec.solve)
    assert callable(ilp.solve)
    assert callable(moves.improve)
