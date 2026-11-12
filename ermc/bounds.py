"""Lower bounds inside a kernel (project document section 5.4).

Three bounds from weakest to strongest: the trivial bound ``L_0`` (sum of the
negative costs), the cycle packing bound, and the integer programming bound
(provided by the solver). This module implements the first two.

Pure: takes a cost matrix, returns a number. Must not import synth, blocking,
features or model (CLAUDE.md invariant 1).
"""

from __future__ import annotations

from . import CostMatrix


def trivial_bound(C: CostMatrix) -> float:
    """Return ``L_0``, the sum of the negative costs of ``C`` (section 2)."""
    raise NotImplementedError


def cycle_packing_bound(C: CostMatrix) -> float:
    """Return the cycle packing lower bound on ``OPT`` for a complete kernel.

    Uses conflicted triangles: ``L_pack = L_0 + P`` where ``P`` is accumulated
    from the smallest residual weight of each conflicted triangle (section 5.4).
    """
    raise NotImplementedError


def lower_bound(C: CostMatrix) -> float:
    """Return the strongest lower bound available without the integer program.

    Currently the maximum of :func:`trivial_bound` and
    :func:`cycle_packing_bound`.
    """
    raise NotImplementedError
