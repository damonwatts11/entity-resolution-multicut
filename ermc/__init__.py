"""ermc: entity resolution by certified decomposition of the minimum cost multicut.

Placeholder package name (see CLAUDE.md). If renamed, rename everywhere in one
commit.

Shared conventions (see CLAUDE.md "Conventions"):

- Records are indexed ``0 .. |V| - 1``.
- Edges are three aligned arrays ``(u, v, c)`` with ``u < v``, ``u, v`` of dtype
  ``int32`` and ``c`` of dtype ``float32``.
- A partition is one ``int`` array of labels of length ``|V|``.
- A kernel is an array of record indices plus a dense symmetric cost matrix with
  zero diagonal.
- Sign convention: positive cost favours joining, negative favours cutting. The
  objective is the sum of the costs of the cut edges.
"""

from __future__ import annotations

from typing import TypeAlias

import numpy as np
import numpy.typing as npt

__version__ = "0.0.0"

# Type aliases used across the package.
Labels: TypeAlias = npt.NDArray[np.int_]
CostMatrix: TypeAlias = npt.NDArray[np.float64]
Edges: TypeAlias = tuple[npt.NDArray[np.int32], npt.NDArray[np.int32], npt.NDArray[np.float32]]

__all__ = ["__version__", "Labels", "CostMatrix", "Edges"]
