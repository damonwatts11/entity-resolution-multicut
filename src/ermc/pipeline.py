"""End-to-end entity-resolution pipeline.

Wires the pieces together:

    records -> pairwise scores -> signed edge weights -> multicut -> clusters

and, when ground truth is available, scores the result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .data import Dataset, Record
from .evaluate import Evaluation, evaluate
from .multicut import MulticutResult, solve_multicut
from .similarity import build_edge_weights, score_pairs


@dataclass
class PipelineResult:
    labels: dict[int, int]            # record_id -> predicted cluster id
    multicut: MulticutResult
    n_candidate_pairs: int
    evaluation: Optional[Evaluation]  # None when no ground truth supplied


def run_pipeline(
    records: list[Record],
    *,
    truth: Optional[dict[int, int]] = None,
    use_blocking: bool = True,
    method: str = "auto",
    time_limit: Optional[float] = None,
) -> PipelineResult:
    """Run the full matcher over ``records``.

    Args:
        records: the records to reconcile (across both systems).
        truth: optional ``{record_id: entity_id}`` for scoring.
        use_blocking: prune candidate pairs by block key before scoring.
        method: multicut backend -- ``"ilp"``, ``"gaec"`` or ``"auto"``.
        time_limit: optional CBC time limit in seconds.

    Returns:
        A :class:`PipelineResult`.
    """
    node_ids = [r.record_id for r in records]

    scores = score_pairs(records, use_blocking=use_blocking)
    weights = build_edge_weights(scores)

    result = solve_multicut(node_ids, weights, method=method,
                            time_limit=time_limit)

    evaluation = evaluate(truth, result.labels) if truth is not None else None
    return PipelineResult(
        labels=result.labels,
        multicut=result,
        n_candidate_pairs=len(scores),
        evaluation=evaluation,
    )


def run_on_dataset(dataset: Dataset, **kwargs) -> PipelineResult:
    """Convenience wrapper: run the pipeline on a generated :class:`Dataset`,
    scoring against its ground truth."""
    return run_pipeline(dataset.records, truth=dataset.truth(), **kwargs)
