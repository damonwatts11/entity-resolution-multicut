"""Exact resolution by integer programming (project document section 8.6).

One binary variable per pair and the triangle inequalities ``x_ij <= x_ik + x_kj``.
Up to about 40 vertices all triangle inequalities are stated at once; beyond that
they are separated lazily: solve, list the violated triangles of the solution,
add them, solve again. A time limit per kernel is enforced; on time-out the best
proven bound is kept as a lower bound and the greedy solution as the partition.
The open solver HiGHS, reached through ``scipy.optimize.milp``, is used.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import CostMatrix, Labels


@dataclass(frozen=True)
class IlpResult:
    """Result of the integer program.

    Attributes:
        labels: the partition found.
        lower_bound: the best proven lower bound (equals the cost of ``labels``
            when the program terminates to optimality).
        optimal: whether the program terminated within the time limit.
    """

    labels: Labels
    lower_bound: float
    optimal: bool


def solve(C: CostMatrix, time_limit: float | None = None) -> IlpResult:
    """Solve the multicut on ``C`` exactly, subject to ``time_limit`` seconds.

    Args:
        C: symmetric cost matrix with zero diagonal, shape ``(s, s)``.
        time_limit: wall-clock budget in seconds, or ``None`` for no limit.

    Returns:
        An :class:`IlpResult`.
    """
    raise NotImplementedError
