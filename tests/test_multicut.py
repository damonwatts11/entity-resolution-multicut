"""Tests for the multicut solvers and the transitivity guarantee."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from ermc.multicut import solve_gaec, solve_ilp, solve_multicut


def _is_valid_partition(nodes, labels):
    return set(labels) == set(nodes)


def test_single_positive_edge_merges():
    nodes = [0, 1]
    weights = {(0, 1): 3.0}
    for method in ("ilp", "gaec"):
        res = solve_multicut(nodes, weights, method=method)
        assert res.labels[0] == res.labels[1]
        assert res.objective == 0.0  # nothing cut


def test_single_negative_edge_splits():
    nodes = [0, 1]
    weights = {(0, 1): -3.0}
    for method in ("ilp", "gaec"):
        res = solve_multicut(nodes, weights, method=method)
        assert res.labels[0] != res.labels[1]


def test_frustrated_triangle_resolved_consistently():
    # Two strong positive edges, one weak negative edge. The negative edge must
    # be ignored (kept uncut) because cutting a single triangle edge is
    # infeasible -- transitivity forces all three together.
    nodes = [0, 1, 2]
    weights = {(0, 1): 5.0, (1, 2): 5.0, (0, 2): -1.0}
    res = solve_ilp(nodes, weights)
    # All three should land in one cluster: breaking the weak edge alone is
    # impossible, and merging costs less than splitting the strong edges.
    assert res.labels[0] == res.labels[1] == res.labels[2]
    assert res.optimal


def test_ilp_result_is_a_valid_partition():
    # A frustrated cycle where naive thresholding would be intransitive.
    nodes = [0, 1, 2, 3]
    weights = {
        (0, 1): 4.0,
        (1, 2): 4.0,
        (2, 3): 4.0,
        (0, 3): -6.0,
        (0, 2): -1.0,
        (1, 3): -1.0,
    }
    res = solve_ilp(nodes, weights)
    assert _is_valid_partition(nodes, res.labels)
    # No triangle may have exactly one cut edge (transitivity).
    from itertools import combinations
    cut = {
        tuple(sorted(p)): (res.labels[p[0]] != res.labels[p[1]])
        for p in combinations(nodes, 2)
    }
    for i, j, k in combinations(nodes, 3):
        c = [cut[tuple(sorted((i, j)))],
             cut[tuple(sorted((i, k)))],
             cut[tuple(sorted((j, k)))]]
        assert sum(c) != 1, "a triangle has exactly one cut edge"


def test_ilp_matches_or_beats_gaec_objective():
    nodes = [0, 1, 2, 3, 4]
    weights = {
        (0, 1): 3.0, (0, 2): 2.0, (1, 2): 2.5,
        (2, 3): -2.0, (3, 4): 4.0, (2, 4): -1.0,
        (0, 4): -3.0, (1, 3): -1.5,
    }
    ilp = solve_ilp(nodes, weights)
    gaec = solve_gaec(nodes, weights)
    # ILP is exact, so its cut cost can never exceed the heuristic's.
    assert ilp.objective <= gaec.objective + 1e-9
    assert ilp.optimal


def test_isolated_nodes_each_own_cluster():
    nodes = [0, 1, 2]
    weights = {}  # no evidence anywhere
    res = solve_multicut(nodes, weights, method="ilp")
    assert len({res.labels[n] for n in nodes}) == 3


def test_decomposition_keeps_large_sparse_instances_exact():
    # 130 nodes but only one scored edge: decomposition leaves 128 singletons
    # plus one 2-node component solved exactly by the ILP.
    nodes = list(range(130))
    weights = {(0, 1): 2.0}
    res = solve_multicut(nodes, weights, method="auto")
    assert _is_valid_partition(nodes, res.labels)
    assert res.labels[0] == res.labels[1]
    assert len(set(res.labels.values())) == 129  # one pair merged, rest apart
    assert res.optimal


def test_large_component_uses_greedy_under_auto():
    # A single dense component bigger than the ILP cap must not be sent to CBC.
    n = 70
    nodes = list(range(n))
    weights = {(i, j): 1.0 for i in range(n) for j in range(i + 1, n)}
    res = solve_multicut(nodes, weights, method="auto")
    # All mutually attracting -> one cluster, found greedily (not proven optimal).
    assert len(set(res.labels.values())) == 1
    assert not res.optimal


def test_clusters_helper_groups_nodes():
    nodes = [0, 1, 2, 3]
    weights = {(0, 1): 5.0, (2, 3): 5.0, (0, 2): -5.0}
    res = solve_ilp(nodes, weights)
    clusters = res.clusters()
    assert [0, 1] in clusters
    assert [2, 3] in clusters
