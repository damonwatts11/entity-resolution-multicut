"""Pairwise classifier and costs (project document sections 7.3, 7.4).

Estimates the probability ``p_uv`` that two records designate the same entity by
logistic regression, calibrates it, and maps it to a clipped logit cost
``c_uv = log(p / (1 - p))`` with ``p`` clipped to ``[eps, 1 - eps]``. The sign of
the cost changes at ``p = 1/2`` (CLAUDE.md invariant 4).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class CostModel:
    """A fitted, calibrated classifier that turns features into costs."""

    eps: float = 1e-4

    def fit(
        self,
        features: npt.NDArray[np.float64],
        labels: npt.NDArray[np.int_],
    ) -> "CostModel":
        """Fit and calibrate on a labelled sample that includes completion pairs.

        ``labels`` here are pair match labels on the dedicated training
        population, not the evaluation partition (CLAUDE.md invariant 2).
        """
        raise NotImplementedError

    def costs(self, features: npt.NDArray[np.float64]) -> npt.NDArray[np.float32]:
        """Return clipped logit costs for ``features``.

        Returns:
            Array of shape ``(m,)``, dtype ``float32``. Positive favours joining.
        """
        raise NotImplementedError
