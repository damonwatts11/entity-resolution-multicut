"""Completion: dense cost matrix of a kernel (project document sections 4.3, 8.2).

Every kernel is turned into a complete graph: pairs that blocking did not propose
are scored, which restores the negative evidence. The kernel is stored as a dense
symmetric cost matrix with zero diagonal.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import numpy.typing as npt

from . import CostMatrix, Edges


def complete(
    kernel: npt.NDArray[np.int32],
    edges: Edges,
    scorer: Callable[[npt.NDArray[np.int32]], npt.NDArray[np.float32]],
) -> CostMatrix:
    """Build the dense cost matrix of ``kernel``.

    Args:
        kernel: array of record indices in the kernel.
        edges: the candidate edges, used to fill known entries.
        scorer: callable mapping an ``(m, 2)`` array of record-index pairs to
            their costs; used to score the pairs blocking did not propose.

    Returns:
        Symmetric ``(s, s)`` cost matrix with zero diagonal, where ``s`` is the
        kernel size.
    """
    raise NotImplementedError
