#!/usr/bin/env python3
"""Demo: generate a synthetic two-system instance, reconcile it with the
minimum-cost multicut, and report accuracy -- optionally against a naive
threshold baseline that ignores transitivity.

Run from the repo root:

    python scripts/run_demo.py --entities 40 --corruption 0.3 --seed 7
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ermc.data import generate_dataset  # noqa: E402
from ermc.evaluate import evaluate  # noqa: E402
from ermc.multicut import _components_from_uncut  # noqa: E402
from ermc.pipeline import run_pipeline  # noqa: E402
from ermc.similarity import build_edge_weights, score_pairs  # noqa: E402


def threshold_baseline(records, weights, threshold: float = 0.0):
    """Naive baseline: join every pair whose weight exceeds ``threshold`` and
    take connected components -- i.e. apply transitivity *after* matching. This
    is exactly what the multicut avoids, so it tends to over-merge via chains.
    """
    node_ids = [r.record_id for r in records]
    uncut = [(i, j) for (i, j), w in weights.items() if w > threshold]
    return _components_from_uncut(node_ids, uncut)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entities", type=int, default=40)
    parser.add_argument("--corruption", type=float, default=0.3)
    parser.add_argument("--overlap", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--method", choices=["ilp", "gaec", "auto"],
                        default="auto")
    parser.add_argument("--no-blocking", action="store_true")
    parser.add_argument("--time-limit", type=float, default=None,
                        help="CBC time limit in seconds (ILP only)")
    args = parser.parse_args()

    ds = generate_dataset(
        n_entities=args.entities,
        corruption_rate=args.corruption,
        overlap=args.overlap,
        seed=args.seed,
    )
    truth = ds.truth()
    print(f"Generated {len(ds.records)} records over {ds.n_entities} entities "
          f"(corruption={args.corruption}, overlap={args.overlap}).\n")

    result = run_pipeline(
        ds.records,
        truth=truth,
        use_blocking=not args.no_blocking,
        method=args.method,
        time_limit=args.time_limit,
    )

    print(f"Candidate pairs scored: {result.n_candidate_pairs}")
    print(f"Multicut method: {result.multicut.method}  "
          f"optimal={result.multicut.optimal}  "
          f"cut_cost={result.multicut.objective:.2f}\n")

    print("=== Minimum-cost multicut ===")
    print(result.evaluation.summary())

    # Baseline for comparison.
    scores = score_pairs(ds.records, use_blocking=not args.no_blocking)
    weights = build_edge_weights(scores)
    base_labels = threshold_baseline(ds.records, weights)
    base_eval = evaluate(truth, base_labels)
    print("\n=== Threshold + transitive-closure baseline ===")
    print(base_eval.summary())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
