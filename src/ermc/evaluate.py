"""Scoring a predicted partition against ground truth.

Two complementary views:

* **Pairwise precision / recall / F1** -- treats every unordered pair of
  records as a binary "same entity?" decision and compares predicted
  co-clustering against the truth. Intuitive and directly tied to the matching
  task.
* **Adjusted Rand Index** -- a chance-corrected clustering agreement score in
  roughly ``[-0.5, 1]`` (1 = identical partitions, 0 = random).

Both are implemented from scratch (no scikit-learn dependency).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb


@dataclass(frozen=True)
class PairwiseScores:
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    false_negatives: int


def _as_label_lists(truth: dict[int, int], pred: dict[int, int]):
    """Align the two labellings over their common keys."""
    keys = sorted(set(truth) & set(pred))
    if set(truth) != set(pred):
        missing = set(truth) ^ set(pred)
        raise ValueError(
            f"truth and prediction cover different nodes; symmetric diff: "
            f"{sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}"
        )
    return keys, [truth[k] for k in keys], [pred[k] for k in keys]


def pairwise_prf(truth: dict[int, int], pred: dict[int, int]) -> PairwiseScores:
    """Pairwise precision, recall and F1 of the predicted co-clustering."""
    keys, t, p = _as_label_lists(truth, pred)
    tp = fp = fn = 0
    for a, b in combinations(range(len(keys)), 2):
        same_truth = t[a] == t[b]
        same_pred = p[a] == p[b]
        if same_pred and same_truth:
            tp += 1
        elif same_pred and not same_truth:
            fp += 1
        elif not same_pred and same_truth:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    return PairwiseScores(precision, recall, f1, tp, fp, fn)


def adjusted_rand_index(truth: dict[int, int], pred: dict[int, int]) -> float:
    """Adjusted Rand Index between the truth and predicted partitions."""
    keys, t, p = _as_label_lists(truth, pred)
    n = len(keys)
    if n < 2:
        return 1.0

    # Contingency table n_ij = |cluster_i(truth) ∩ cluster_j(pred)|.
    contingency: dict[tuple[int, int], int] = {}
    a_counts: dict[int, int] = {}
    b_counts: dict[int, int] = {}
    for ti, pi in zip(t, p):
        contingency[(ti, pi)] = contingency.get((ti, pi), 0) + 1
        a_counts[ti] = a_counts.get(ti, 0) + 1
        b_counts[pi] = b_counts.get(pi, 0) + 1

    sum_comb = sum(comb(v, 2) for v in contingency.values())
    sum_a = sum(comb(v, 2) for v in a_counts.values())
    sum_b = sum(comb(v, 2) for v in b_counts.values())
    total = comb(n, 2)

    expected = sum_a * sum_b / total
    max_index = 0.5 * (sum_a + sum_b)
    if max_index == expected:  # both partitions trivial
        return 1.0
    return (sum_comb - expected) / (max_index - expected)


@dataclass(frozen=True)
class Evaluation:
    pairwise: PairwiseScores
    ari: float
    n_records: int
    n_true_entities: int
    n_pred_clusters: int

    def summary(self) -> str:
        pw = self.pairwise
        return (
            f"records={self.n_records}  "
            f"true_entities={self.n_true_entities}  "
            f"pred_clusters={self.n_pred_clusters}\n"
            f"pairwise  P={pw.precision:.3f}  R={pw.recall:.3f}  "
            f"F1={pw.f1:.3f}  (tp={pw.true_positives} "
            f"fp={pw.false_positives} fn={pw.false_negatives})\n"
            f"ARI={self.ari:.3f}"
        )


def evaluate(truth: dict[int, int], pred: dict[int, int]) -> Evaluation:
    """Full evaluation bundle for a predicted partition."""
    pw = pairwise_prf(truth, pred)
    ari = adjusted_rand_index(truth, pred)
    return Evaluation(
        pairwise=pw,
        ari=ari,
        n_records=len(truth),
        n_true_entities=len(set(truth.values())),
        n_pred_clusters=len(set(pred.values())),
    )
