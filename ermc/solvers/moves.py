"""Local search by vertex moves (project document section 8.5).

Starting from a partition, moves a vertex to another cluster or to a new empty
cluster whenever the move strictly lowers the cost. Sweeps repeat until no move
applies. Kernighan-Lin with joins is the stronger variant and is optional.
"""

from __future__ import annotations

from .. import CostMatrix, Labels


def improve(C: CostMatrix, labels: Labels) -> Labels:
    """Improve ``labels`` on ``C`` by vertex moves until no move lowers the cost.

    Args:
        C: symmetric cost matrix with zero diagonal, shape ``(s, s)``.
        labels: starting partition, integer labels of length ``s``.

    Returns:
        Integer labels of length ``s`` whose cost is at most that of ``labels``.
    """
    raise NotImplementedError
