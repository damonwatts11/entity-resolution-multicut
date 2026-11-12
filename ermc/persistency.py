"""Persistency reduction (project document section 8.3, proposition 2).

Contracts edges that satisfy the persistency criterion, which provably preserves
the optimum. The reduction is sequential: contract one edge, update the matrix,
test again. Never contract several edges sharing a vertex from one evaluation of
the criterion (CLAUDE.md invariant 7).

Pure: takes a cost matrix, returns a cost matrix and a grouping. Must not import
synth, blocking, features or model (CLAUDE.md invariant 1).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from . import CostMatrix


def reduce(C: CostMatrix) -> tuple[CostMatrix, list[npt.NDArray[np.int_]]]:
    """Reduce ``C`` by persistency contraction.

    Args:
        C: symmetric cost matrix with zero diagonal, shape ``(s, s)``.

    Returns:
        A pair ``(C_reduced, groups)`` where ``C_reduced`` is the contracted
        matrix of shape ``(t, t)`` with ``t <= s``, and ``groups`` maps each
        reduced vertex to the array of original vertices it absorbs, so that a
        partition of the reduced matrix lifts back to a partition of ``C``.
    """
    raise NotImplementedError
