"""Kernel formation: capped union (project document section 8.1).

Kruskal on the positive edges in decreasing order of cost, with a cap ``B`` on
the size of any merged set. Positive edges left between two kernels are abandoned
and their total cost is the decomposition gap ``Delta``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from . import Edges


@dataclass(frozen=True)
class Kernels:
    """The kernels and the abandoned positive cost.

    Attributes:
        members: list of arrays of record indices, one per kernel, each of size
            at most ``B``.
        delta: total cost of the abandoned positive edges (``Delta >= 0``).
    """

    members: list[npt.NDArray[np.int32]]
    delta: float


def form_kernels(edges: Edges, B: int) -> Kernels:
    """Form kernels of at most ``B`` records from ``edges``.

    Args:
        edges: the candidate edges ``(u, v, c)``.
        B: the cap on kernel size, the single parameter of the method.

    Returns:
        A :class:`Kernels`.
    """
    raise NotImplementedError
