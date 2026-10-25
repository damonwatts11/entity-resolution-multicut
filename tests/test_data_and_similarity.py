"""Tests for synthetic data generation and pairwise scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from ermc.data import Record, generate_dataset
from ermc.similarity import (
    build_edge_weights,
    score_pair,
    score_pairs,
    string_sim,
)


def test_generate_is_reproducible():
    a = generate_dataset(n_entities=20, seed=42)
    b = generate_dataset(n_entities=20, seed=42)
    assert [r.record_id for r in a.records] == [r.record_id for r in b.records]
    assert a.truth() == b.truth()


def test_every_entity_emits_at_least_one_record():
    ds = generate_dataset(n_entities=30, seed=1)
    entities = {r.entity_id for r in ds.records}
    assert entities == set(range(30))


def test_record_ids_are_unique_and_contiguous():
    ds = generate_dataset(n_entities=15, seed=3)
    ids = sorted(r.record_id for r in ds.records)
    assert ids == list(range(len(ids)))


def test_corruption_rate_bounds_validated():
    with pytest.raises(ValueError):
        generate_dataset(corruption_rate=1.5)
    with pytest.raises(ValueError):
        generate_dataset(overlap=-0.1)


def test_string_sim_bounds():
    assert string_sim("abc", "abc") == 1.0
    assert string_sim("", "") == 1.0
    assert string_sim("abc", "") == 0.0
    assert 0.0 < string_sim("Smith", "Smyth") < 1.0


def _rec(rid, **kw):
    base = dict(
        record_id=rid, entity_id=0, source="A",
        first_name="John", last_name="Smith", dob="1980-01-01",
        street="12 Oak Ave", city="Springfield", state="IL",
        zip_code="62701", email="john.smith@example.com",
    )
    base.update(kw)
    return Record(**base)


def test_identical_records_score_strongly_positive():
    a, b = _rec(0), _rec(1)
    s = score_pair(a, b)
    assert s.weight > 0
    assert s.prob > 0.9


def test_disjoint_records_score_negative():
    a = _rec(0)
    b = _rec(1, first_name="Mary", last_name="Jones", dob="1999-12-31",
             street="900 Pine Rd", city="Salem", state="OR",
             zip_code="97301", email="mary.jones@example.com")
    s = score_pair(a, b)
    assert s.weight < 0
    assert s.prob < 0.1


def test_missing_fields_contribute_no_evidence():
    # Two records agreeing on name but with everything else missing should sit
    # closer to the prior than a full agreement.
    full = score_pair(_rec(0), _rec(1))
    sparse_a = _rec(0, dob=None, street=None, city=None, zip_code=None, email=None)
    sparse_b = _rec(1, dob=None, street=None, city=None, zip_code=None, email=None)
    sparse = score_pair(sparse_a, sparse_b)
    assert sparse.weight < full.weight


def test_score_pairs_orders_endpoints():
    ds = generate_dataset(n_entities=10, seed=5)
    scores = score_pairs(ds.records)
    assert all(s.i < s.j for s in scores)
    weights = build_edge_weights(scores)
    assert all(i < j for (i, j) in weights)


def test_blocking_reduces_candidate_count():
    ds = generate_dataset(n_entities=40, seed=9)
    blocked = score_pairs(ds.records, use_blocking=True)
    full = score_pairs(ds.records, use_blocking=False)
    assert len(blocked) <= len(full)
