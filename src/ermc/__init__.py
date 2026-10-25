"""Entity resolution via minimum-cost multicut.

A small, self-contained pipeline that reconciles records across two systems by
posing the partitioning as a minimum-cost multicut (equivalently, correlation
clustering) in which the transitivity of the "same entity" relation is encoded
directly in the optimisation model rather than repaired after the fact.
"""

from .data import Record, generate_dataset
from .similarity import PairScore, score_pairs, build_edge_weights
from .multicut import solve_multicut, MulticutResult
from .evaluate import pairwise_prf, adjusted_rand_index, evaluate
from .pipeline import run_pipeline, PipelineResult

__all__ = [
    "Record",
    "generate_dataset",
    "PairScore",
    "score_pairs",
    "build_edge_weights",
    "solve_multicut",
    "MulticutResult",
    "pairwise_prf",
    "adjusted_rand_index",
    "evaluate",
    "run_pipeline",
    "PipelineResult",
]
