"""Tests for evaluation metrics and the end-to-end pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from ermc.data import generate_dataset
from ermc.evaluate import adjusted_rand_index, evaluate, pairwise_prf
from ermc.pipeline import run_pipeline


def test_perfect_prediction_scores_one():
    truth = {0: 0, 1: 0, 2: 1, 3: 1}
    pred = {0: 5, 1: 5, 2: 9, 3: 9}  # same partition, different labels
    pw = pairwise_prf(truth, pred)
    assert pw.precision == 1.0 and pw.recall == 1.0 and pw.f1 == 1.0
    assert adjusted_rand_index(truth, pred) == 1.0


def test_over_merge_hurts_precision():
    truth = {0: 0, 1: 0, 2: 1, 3: 1}
    pred = {0: 0, 1: 0, 2: 0, 3: 0}  # everything merged
    pw = pairwise_prf(truth, pred)
    assert pw.recall == 1.0
    assert pw.precision < 1.0


def test_over_split_hurts_recall():
    truth = {0: 0, 1: 0, 2: 0}
    pred = {0: 0, 1: 1, 2: 2}  # all singletons
    pw = pairwise_prf(truth, pred)
    assert pw.precision == 1.0
    assert pw.recall == 0.0


def test_mismatched_keys_raise():
    with pytest.raises(ValueError):
        pairwise_prf({0: 0, 1: 0}, {0: 0, 2: 1})


def test_ari_of_random_is_near_zero():
    # Independently random labellings should sit near 0, not near 1.
    import random
    rng = random.Random(0)
    truth = {i: rng.randrange(4) for i in range(200)}
    pred = {i: rng.randrange(4) for i in range(200)}
    ari = adjusted_rand_index(truth, pred)
    assert -0.2 < ari < 0.2


def test_pipeline_recovers_entities_on_easy_data():
    # Low corruption: the multicut should reconstruct entities almost exactly.
    ds = generate_dataset(n_entities=25, corruption_rate=0.1, seed=11)
    result = run_pipeline(ds.records, truth=ds.truth(), method="ilp")
    assert result.evaluation is not None
    assert result.evaluation.pairwise.f1 > 0.85
    assert result.evaluation.ari > 0.85


def test_pipeline_without_truth_skips_evaluation():
    ds = generate_dataset(n_entities=10, seed=2)
    result = run_pipeline(ds.records, method="gaec")
    assert result.evaluation is None
    assert set(result.labels) == {r.record_id for r in ds.records}


def test_pipeline_beats_or_matches_singletons_baseline():
    # F1 should comfortably exceed the degenerate all-singletons partition.
    ds = generate_dataset(n_entities=20, corruption_rate=0.3, seed=4)
    result = run_pipeline(ds.records, truth=ds.truth(), method="ilp")
    singletons = {rid: rid for rid in ds.truth()}
    base = evaluate(ds.truth(), singletons)
    assert result.evaluation.pairwise.f1 >= base.pairwise.f1
