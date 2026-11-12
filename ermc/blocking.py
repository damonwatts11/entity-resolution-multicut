"""Blocking: candidate pair generation (project document section 7.1).

Reduces the set of all pairs to a candidate set ``E`` by the union of several
blocking keys, and supports a single record lookup for the incremental mode.
Reports reduction ratio, pair completeness and the share of true non-matches.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pandas as pd


def candidates(records: pd.DataFrame) -> npt.NDArray[np.int32]:
    """Return candidate pairs as an ``(m, 2)`` array of record indices, ``u < v``.

    Args:
        records: the record table, indexed ``0 .. |V| - 1``.

    Returns:
        Integer array of shape ``(m, 2)``, dtype ``int32``, each row ``(u, v)``
        with ``u < v``, sorted and unique.
    """
    raise NotImplementedError


def lookup(record: pd.Series) -> npt.NDArray[np.int32]:
    """Return existing record indices that share a blocking key with ``record``.

    Used by the incremental mode (section 9) to score only the relevant pairs.
    """
    raise NotImplementedError
