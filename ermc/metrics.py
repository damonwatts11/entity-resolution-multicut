"""Evaluation metrics (project document section 12.2).

The primary metric is the variation of information between the true partition and
the predicted partition, with its false-merge and false-split terms reported
separately. Pairwise precision, recall and F1 are secondary. This is the only
module, besides classifier training on the training population, that may read the
true partition (CLAUDE.md invariant 2).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt


def vi(a: npt.NDArray[np.int_], b: npt.NDArray[np.int_]) -> tuple[float, float]:
    """Variation of information between partitions ``a`` (true) and ``b`` (predicted).

    Returns:
        A pair ``(false_merges, false_splits)`` whose sum is the variation of
        information; ``false_merges = H(a | b)`` and ``false_splits = H(b | a)``.
    """
    raise NotImplementedError


def pairwise(a: npt.NDArray[np.int_], b: npt.NDArray[np.int_]) -> tuple[float, float, float]:
    """Pairwise precision, recall and F1 of predicted ``b`` against true ``a``.

    Returns:
        A triple ``(precision, recall, f1)``.
    """
    raise NotImplementedError
