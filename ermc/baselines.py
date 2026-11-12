"""Baselines (project document section 12.1).

Reference procedures to compare certified decomposition against: thresholding
with transitive closure, thresholding without closure, and hierarchical
agglomerative clustering with average linkage. Each is one function on the
candidate graph.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from . import Edges


def transitive_closure(edges: Edges, n: int) -> npt.NDArray[np.int_]:
    """Threshold at ``p = 1/2`` (cost ``> 0``) then take connected components.

    Args:
        edges: the candidate edges ``(u, v, c)``.
        n: the number of records.

    Returns:
        A partition as an ``int`` array of labels of length ``n``.
    """
    raise NotImplementedError


def thresholding(edges: Edges, n: int) -> npt.NDArray[np.int_]:
    """Threshold without closure: keep the positive relation, leave it intransitive."""
    raise NotImplementedError


def average_linkage(edges: Edges, n: int) -> npt.NDArray[np.int_]:
    """Average linkage on ``1 - p`` inside the components of the positive subgraph."""
    raise NotImplementedError
