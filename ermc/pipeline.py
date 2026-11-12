"""The batch pipeline: steps 1 to 7 with the certificate (project document sections 4, 5.5, 8.7).

Blocking and scoring, kernel formation, completion, reduction, resolution,
bounding and assembly. Runs the per-kernel work in parallel over a process pool
and returns a partition with the certificate ``(U, L, Delta, gamma)``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import pandas as pd


@dataclass(frozen=True)
class Certificate:
    """The certificate reported by the pipeline (section 5.5)."""

    U: float  # upper bound: cost of the returned partition
    L: float  # lower bound
    delta: float  # decomposition gap
    gamma: float  # relative gap in [0, 1]


@dataclass(frozen=True)
class Resolution:
    """The output of the pipeline."""

    labels: npt.NDArray[np.int_]
    certificate: Certificate


def resolve(records: pd.DataFrame, B: int) -> Resolution:
    """Resolve ``records`` by certified decomposition with cap ``B``.

    Args:
        records: the record table, indexed ``0 .. |V| - 1``.
        B: the cap on kernel size.

    Returns:
        A :class:`Resolution` with the partition and its certificate.
    """
    raise NotImplementedError
