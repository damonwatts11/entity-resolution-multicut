"""Pairwise record comparison and signed edge weights.

Each candidate pair of records is scored field-by-field, the per-field
agreements are combined into a match probability in the spirit of the
Fellegi--Sunter model, and that probability is turned into a *signed log-odds
weight*:

    w = log( p / (1 - p) )

A positive weight is evidence that the two records denote the *same* entity
(so cutting the edge should cost); a negative weight is evidence they are
*different* (so cutting the edge should pay). These weights are exactly the
input the minimum-cost multicut consumes. Crucially, the pairwise scores are
produced independently, so they are frequently intransitive (A~B, B~C, but
A!~C) -- the inconsistency the multicut is there to reconcile.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import combinations
from typing import Iterable, Optional

from .data import Record


# How much each field's agreement moves the log-odds. These are hand-set
# (rather than learned) but reflect the usual discriminating power: email and
# date-of-birth are strong identifiers, a first name much weaker.
_FIELD_WEIGHTS = {
    "last_name": 2.2,
    "first_name": 1.3,
    "dob": 3.0,
    "zip_code": 1.6,
    "street": 1.4,
    "city": 0.6,
    "email": 3.2,
}

# Baseline log-odds for a pair before any evidence. Negative because, a priori,
# two arbitrary records are far more likely to be different entities than the
# same one.
_PRIOR_LOG_ODDS = -4.0

# Clamp to keep weights finite and the ILP objective well-conditioned.
_WEIGHT_CLAMP = 8.0


def _norm(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def string_sim(a: Optional[str], b: Optional[str]) -> float:
    """Normalised string similarity in ``[0, 1]`` (1.0 = identical).

    Uses :class:`difflib.SequenceMatcher`, which is a reasonable, dependency-free
    stand-in for edit-distance-based ratios.
    """
    a_n, b_n = _norm(a), _norm(b)
    if not a_n and not b_n:
        return 1.0
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def _field_agreement(a: Optional[str], b: Optional[str], *,
                     exact: bool = False) -> Optional[float]:
    """Return an agreement signal in ``[-1, 1]`` for one field, or ``None`` if
    the field is missing on either side (missing == no evidence).

    ``+1`` means strong agreement, ``-1`` strong disagreement; the midpoint is
    ~0.5 similarity which contributes nothing.
    """
    if a is None or b is None or _norm(a) == "" or _norm(b) == "":
        return None
    if exact:
        return 1.0 if _norm(a) == _norm(b) else -1.0
    sim = string_sim(a, b)
    # Map similarity [0,1] onto [-1,1], centred so near-misses stay mildly
    # positive and clear mismatches pull negative.
    return 2.0 * sim - 1.0


@dataclass(frozen=True)
class PairScore:
    """Scored comparison of two records."""

    i: int  # record_id, with i < j
    j: int
    log_odds: float
    prob: float

    @property
    def weight(self) -> float:
        """Signed edge weight for the multicut (same as ``log_odds``)."""
        return self.log_odds


def score_pair(a: Record, b: Record) -> PairScore:
    """Score a single record pair into a signed log-odds weight."""
    log_odds = _PRIOR_LOG_ODDS
    comparisons = {
        "first_name": _field_agreement(a.first_name, b.first_name),
        "last_name": _field_agreement(a.last_name, b.last_name),
        "dob": _field_agreement(a.dob, b.dob),
        "zip_code": _field_agreement(a.zip_code, b.zip_code),
        "street": _field_agreement(a.street, b.street),
        "city": _field_agreement(a.city, b.city),
        "email": _field_agreement(a.email, b.email),
    }
    for field_name, agreement in comparisons.items():
        if agreement is None:
            continue
        log_odds += _FIELD_WEIGHTS[field_name] * agreement

    log_odds = max(-_WEIGHT_CLAMP, min(_WEIGHT_CLAMP, log_odds))
    prob = 1.0 / (1.0 + math.exp(-log_odds))
    i, j = (a.record_id, b.record_id)
    if i > j:
        i, j = j, i
    return PairScore(i=i, j=j, log_odds=log_odds, prob=prob)


def _block_key(r: Record) -> tuple:
    """Blocking key to prune obviously unrelated pairs.

    Records only compared if they share a block. We block on state plus the
    first character of the (normalised) last name -- cheap and tolerant of most
    single-character corruptions elsewhere.
    """
    last = _norm(r.last_name)
    return (_norm(r.state), last[:1])


def score_pairs(records: Iterable[Record], *,
                use_blocking: bool = True) -> list[PairScore]:
    """Score candidate record pairs.

    Args:
        records: the records to compare.
        use_blocking: when True, only compare records sharing a block key,
            which keeps the candidate set near-linear instead of quadratic.

    Returns:
        A list of :class:`PairScore`, one per compared pair.
    """
    records = list(records)
    scores: list[PairScore] = []

    if use_blocking:
        blocks: dict[tuple, list[Record]] = {}
        for r in records:
            blocks.setdefault(_block_key(r), []).append(r)
        groups = blocks.values()
    else:
        groups = [records]

    for group in groups:
        for a, b in combinations(group, 2):
            scores.append(score_pair(a, b))
    return scores


def build_edge_weights(scores: Iterable[PairScore]) -> dict[tuple[int, int], float]:
    """Collapse pair scores into a ``{(i, j): weight}`` map with ``i < j``."""
    weights: dict[tuple[int, int], float] = {}
    for s in scores:
        i, j = (s.i, s.j) if s.i < s.j else (s.j, s.i)
        weights[(i, j)] = s.weight
    return weights
