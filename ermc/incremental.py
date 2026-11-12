"""Incremental mode: state and insertion (project document section 9).

Inserts one record at a time and touches only the kernels that the record is
positively linked to. Work per insertion is bounded by a function of ``B`` and
does not depend on the population size, apart from the blocking lookup. Deletions
and modifications are out of scope.
"""

from __future__ import annotations

import pandas as pd


class Resolver:
    """Stateful resolver supporting single record insertion (section 9.1, 9.2).

    State: the blocking index, the kernel and entity id of every record, the cost
    matrix and bounds ``U_K``, ``L_K`` of every kernel, and the running values of
    ``Delta``, ``U`` and ``L``.
    """

    def __init__(self, B: int) -> None:
        self.B = B
        raise NotImplementedError

    def insert(self, record: pd.Series) -> int:
        """Insert ``record`` and return its entity id.

        Follows the eight steps of section 9.2: candidates, touched kernels,
        region, completion, resolution, safeguard, identifiers, certificate.
        """
        raise NotImplementedError
