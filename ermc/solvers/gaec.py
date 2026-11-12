"""Greedy additive edge contraction (project document section 8.4).

Repeatedly contracts the most attractive pair while its cost is positive. On a
dense matrix this simple form costs ``O(s^3)`` per kernel, acceptable for ``B``
up to a few hundred.
"""

from __future__ import annotations

from .. import CostMatrix, Labels


def solve(C: CostMatrix) -> Labels:
    """Return a partition of ``C`` by greedy additive edge contraction.

    Args:
        C: symmetric cost matrix with zero diagonal, shape ``(s, s)``.

    Returns:
        Integer labels of length ``s``.
    """
    raise NotImplementedError
