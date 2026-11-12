"""Pairwise similarity features (project document section 7.2).

Computes a vector of similarity features for a batch of pairs: Jaro-Winkler and
normalized Levenshtein on name fields, token Jaccard on the address, calendar
distance on the date of birth, agreement indicators and a missingness indicator
per field. The same function scores blocking pairs and completion pairs so that
all costs are comparable.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pandas as pd


def featurize(records: pd.DataFrame, pairs: npt.NDArray[np.int32]) -> npt.NDArray[np.float64]:
    """Compute the feature matrix for ``pairs`` drawn from ``records``.

    Args:
        records: the record table, indexed ``0 .. |V| - 1``.
        pairs: ``(m, 2)`` array of record indices, dtype ``int32``.

    Returns:
        Feature matrix of shape ``(m, d)``, dtype ``float64``, one row per pair.
    """
    raise NotImplementedError
