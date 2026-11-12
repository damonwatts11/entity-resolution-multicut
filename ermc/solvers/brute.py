"""Brute-force solver, for tests only (project document section 11).

Enumerates all partitions of a set, feasible up to 8 vertices (4140 partitions)
and tolerable at 9 (21147). It is the reference for optimality in the property
tests; never weaken an assertion to make a test pass (CLAUDE.md testing rules).
"""

from __future__ import annotations

from .. import CostMatrix, Labels


def solve(C: CostMatrix) -> Labels:
    """Return an exact optimal partition of ``C`` by enumeration.

    Args:
        C: symmetric cost matrix with zero diagonal, shape ``(s, s)``, with
            ``s`` small (at most 9).

    Returns:
        Integer labels of length ``s`` of minimum cost.
    """
    raise NotImplementedError
