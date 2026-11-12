"""Synthetic data generator (project document section 6.1).

Generates a population of entities with an attribute record, samples observations
across two systems through a corruption model of severity ``theta``, and controls
the density ``rho`` of confusable entities. The true partition is returned for
evaluation only and must never be passed to a pipeline step (CLAUDE.md invariant
2).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Population:
    """A generated population.

    Attributes:
        records: table of observed records, one row per record, indexed
            ``0 .. |V| - 1``.
        true_labels: integer entity id per record. Evaluation only.
    """

    records: pd.DataFrame
    true_labels: "pd.Series[int]"


def generate(n: int, theta: float, rho: float, seed: int) -> Population:
    """Generate ``n`` entities with corruption ``theta`` and confusable density ``rho``.

    Args:
        n: number of true entities.
        theta: corruption severity, governs character, token and field level noise.
        rho: density of confusable entities (households, group subsidiaries).
        seed: integer seed; the generation is fully determined by it.

    Returns:
        A :class:`Population`.
    """
    raise NotImplementedError
