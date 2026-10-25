"""Minimum-cost multicut solver.

Given a set of nodes and signed edge weights ``w_ij`` (positive = evidence the
endpoints are the *same* entity, negative = evidence they are *different*), we
partition the nodes so as to minimise the total weight of the edges that are
*cut* (i.e. whose endpoints end up in different clusters):

    minimise   sum_{i<j} w_ij * x_ij
    s.t.       x_ij in {0, 1}                       (1 = edge i-j is cut)
               x_ij <= x_ik + x_kj   for all i,j,k  (triangle / transitivity)

Cutting a positive edge adds ``w_ij > 0`` to the objective (discouraged);
cutting a negative edge adds ``w_ij < 0`` (rewarded). The triangle inequalities
are the whole point: they force the set of *uncut* edges to be transitive, so
the solution is always a valid partition into entities -- transitivity is a
constraint of the model, never a post-hoc repair.

Two backends are provided:

* :func:`solve_ilp` -- exact, via PuLP + CBC. Adds one binary per node pair and
  the three triangle inequalities per triple. Correct but combinatorial.
* :func:`solve_gaec` -- Greedy Additive Edge Contraction, a fast, dependency-
  light heuristic that always returns a valid partition.

:func:`solve_multicut` dispatches between them.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Optional


@dataclass
class MulticutResult:
    """Outcome of a multicut solve."""

    labels: dict[int, int]  # node -> cluster id
    objective: float        # total weight of cut edges
    method: str             # "ilp" or "gaec"
    optimal: bool           # True only when solved to proven optimality

    def clusters(self) -> list[list[int]]:
        """Nodes grouped by cluster id, each group sorted."""
        groups: dict[int, list[int]] = {}
        for node, label in self.labels.items():
            groups.setdefault(label, []).append(node)
        return [sorted(g) for g in sorted(groups.values(), key=lambda g: min(g))]


def _normalise_weights(
    nodes: list[int],
    weights: dict[tuple[int, int], float],
) -> dict[tuple[int, int], float]:
    """Return weights keyed by ordered ``(i, j)`` with ``i < j``, restricted to
    the given node set."""
    node_set = set(nodes)
    out: dict[tuple[int, int], float] = {}
    for (i, j), w in weights.items():
        if i not in node_set or j not in node_set:
            continue
        a, b = (i, j) if i < j else (j, i)
        out[(a, b)] = out.get((a, b), 0.0) + w
    return out


def _cut_objective(nodes: list[int], weights: dict[tuple[int, int], float],
                   labels: dict[int, int]) -> float:
    total = 0.0
    for (i, j), w in weights.items():
        if labels[i] != labels[j]:
            total += w
    return total


def _components_from_uncut(nodes: list[int],
                           uncut: Iterable[tuple[int, int]]) -> dict[int, int]:
    """Union-find over the uncut edges -> contiguous cluster labels."""
    parent = {n: n for n in nodes}

    def find(x: int) -> int:
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:  # path compression
            parent[x], x = root, parent[x]
        return root

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, j in uncut:
        union(i, j)

    roots = {n: find(n) for n in nodes}
    relabel: dict[int, int] = {}
    labels: dict[int, int] = {}
    for n in nodes:
        r = roots[n]
        if r not in relabel:
            relabel[r] = len(relabel)
        labels[n] = relabel[r]
    return labels


# --------------------------------------------------------------------------- #
# Exact ILP backend
# --------------------------------------------------------------------------- #
def solve_ilp(
    nodes: list[int],
    weights: dict[tuple[int, int], float],
    *,
    default_weight: float = -1e-3,
    time_limit: Optional[float] = None,
    msg: bool = False,
) -> MulticutResult:
    """Solve the minimum-cost multicut exactly as a binary ILP.

    Works on the *complete* graph over ``nodes``: every unscored pair is given
    ``default_weight`` so the triangle inequalities alone certify a valid
    partition. ``default_weight`` is a small *negative* value that encodes the
    prior "no evidence => different entities": when two records were never
    compared (or scored exactly zero), the solver prefers to keep them apart.
    It is negligible next to real evidence, so it only ever breaks ties.
    """
    import pulp

    # Sort so every pair from ``combinations`` is already (i < j); this keeps
    # the variable keys and the sorted lookups in the triangle loop consistent.
    nodes = sorted(nodes)
    w = _normalise_weights(nodes, weights)

    prob = pulp.LpProblem("min_cost_multicut", pulp.LpMinimize)

    # One binary cut variable per unordered pair (complete graph).
    x: dict[tuple[int, int], "pulp.LpVariable"] = {}
    for i, j in combinations(nodes, 2):
        x[(i, j)] = pulp.LpVariable(f"x_{i}_{j}", cat="Binary")

    # Objective: total weight of cut edges. Absent pairs take ``default_weight``.
    prob += pulp.lpSum(w.get(pair, default_weight) * var
                       for pair, var in x.items())

    # Triangle / transitivity constraints: on each triple, no single edge may
    # be cut on its own.
    for i, j, k in combinations(nodes, 3):
        xij = x[tuple(sorted((i, j)))]
        xik = x[tuple(sorted((i, k)))]
        xjk = x[tuple(sorted((j, k)))]
        prob += xij <= xik + xjk
        prob += xik <= xij + xjk
        prob += xjk <= xij + xik

    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit)
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    uncut = [pair for pair, var in x.items() if (var.value() or 0.0) < 0.5]
    labels = _components_from_uncut(nodes, uncut)
    objective = _cut_objective(nodes, w, labels)
    return MulticutResult(
        labels=labels,
        objective=objective,
        method="ilp",
        optimal=(status == "Optimal"),
    )


# --------------------------------------------------------------------------- #
# Greedy Additive Edge Contraction (heuristic backend)
# --------------------------------------------------------------------------- #
def solve_gaec(
    nodes: list[int],
    weights: dict[tuple[int, int], float],
) -> MulticutResult:
    """Greedy Additive Edge Contraction.

    Repeatedly contract the node pair with the most positive connecting weight,
    summing edges to shared neighbours, until no positive edge remains. Fast,
    needs no solver, and always yields a valid partition (though not
    necessarily the optimum).
    """
    nodes = list(nodes)
    w = _normalise_weights(nodes, weights)

    # Adjacency of current (super)node weights.
    adj: dict[int, dict[int, float]] = {n: {} for n in nodes}
    for (i, j), weight in w.items():
        adj[i][j] = weight
        adj[j][i] = weight

    # Union-find so we can report original-node labels at the end.
    parent = {n: n for n in nodes}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    alive = set(nodes)
    while True:
        # Find the strongest positive edge among live supernodes.
        best_pair: Optional[tuple[int, int]] = None
        best_w = 0.0
        for u in alive:
            for v, weight in adj[u].items():
                if v in alive and weight > best_w:
                    best_w = weight
                    best_pair = (u, v)
        if best_pair is None:  # no attractive edge left
            break

        u, v = best_pair
        # Merge v into u.
        parent[find(v)] = find(u)
        alive.discard(v)
        for nbr, weight in adj[v].items():
            if nbr == u:
                continue
            adj[u][nbr] = adj[u].get(nbr, 0.0) + weight
            adj[nbr][u] = adj[nbr].get(u, 0.0) + weight
            adj[nbr].pop(v, None)
        adj[u].pop(v, None)
        adj.pop(v, None)

    labels_raw = {n: find(n) for n in nodes}
    relabel: dict[int, int] = {}
    labels: dict[int, int] = {}
    for n in nodes:
        r = labels_raw[n]
        if r not in relabel:
            relabel[r] = len(relabel)
        labels[n] = relabel[r]

    objective = _cut_objective(nodes, w, labels)
    return MulticutResult(labels=labels, objective=objective,
                          method="gaec", optimal=False)


# The exact ILP has O(k^3) triangle constraints over a k-node component; beyond
# this size "auto" hands the component to the greedy heuristic instead.
_AUTO_ILP_CAP = 60


def _candidate_components(
    nodes: list[int],
    weights: dict[tuple[int, int], float],
) -> list[list[int]]:
    """Connected components of the graph whose edges are the *scored* pairs.

    Unscored pairs carry only the tiny separation default, so nodes in
    different components are always kept apart by the optimum -- each component
    can therefore be solved independently, which is what makes the exact ILP
    tractable at scale.
    """
    node_set = set(nodes)
    edges = [(i, j) for (i, j) in weights if i in node_set and j in node_set]
    labels = _components_from_uncut(nodes, edges)
    groups: dict[int, list[int]] = {}
    for n in nodes:
        groups.setdefault(labels[n], []).append(n)
    return list(groups.values())


def _solve_component(
    comp_nodes: list[int],
    weights: dict[tuple[int, int], float],
    *,
    method: str,
    default_weight: float,
    time_limit: Optional[float],
    msg: bool,
) -> MulticutResult:
    chosen = method
    if chosen == "auto":
        chosen = "ilp" if len(comp_nodes) <= _AUTO_ILP_CAP else "gaec"
    if chosen == "ilp":
        try:
            return solve_ilp(comp_nodes, weights, default_weight=default_weight,
                             time_limit=time_limit, msg=msg)
        except Exception:  # pragma: no cover - solver/import failure fallback
            return solve_gaec(comp_nodes, weights)
    if chosen == "gaec":
        return solve_gaec(comp_nodes, weights)
    raise ValueError(f"unknown method: {method!r}")


def solve_multicut(
    nodes: Iterable[int],
    weights: dict[tuple[int, int], float],
    *,
    method: str = "auto",
    default_weight: float = -1e-3,
    decompose: bool = True,
    time_limit: Optional[float] = None,
    msg: bool = False,
) -> MulticutResult:
    """Partition ``nodes`` by minimum-cost multicut.

    Args:
        nodes: all node ids (records) to cluster.
        weights: ``{(i, j): w}`` signed edge weights (missing pairs default to
            a small negative tie-breaker, i.e. "keep apart").
        method: ``"ilp"`` for the exact CBC solve, ``"gaec"`` for the greedy
            heuristic, or ``"auto"`` to pick per component by its size.
        default_weight: tie-breaking weight for unscored pairs (ILP only);
            small and negative so "no evidence" means "keep apart".
        decompose: solve each connected component of the candidate graph
            independently (always exact and far faster). Disable only to force
            a single monolithic solve.
        time_limit: optional CBC time limit (seconds); ILP only.
        msg: pass solver log through to stdout; ILP only.

    Returns:
        A :class:`MulticutResult`. ``optimal`` is True only if every component
        was solved to proven optimality.
    """
    nodes = list(nodes)
    if method not in ("ilp", "gaec", "auto"):
        raise ValueError(f"unknown method: {method!r}")

    if not decompose:
        return _solve_component(nodes, weights, method=method,
                                default_weight=default_weight,
                                time_limit=time_limit, msg=msg)

    components = _candidate_components(nodes, weights)
    labels: dict[int, int] = {}
    objective = 0.0
    optimal = True
    next_label = 0

    for comp in components:
        if len(comp) == 1:
            labels[comp[0]] = next_label
            next_label += 1
            continue
        comp_set = set(comp)
        comp_weights = {
            (i, j): w for (i, j), w in weights.items()
            if i in comp_set and j in comp_set
        }
        sub = _solve_component(comp, comp_weights, method=method,
                               default_weight=default_weight,
                               time_limit=time_limit, msg=msg)
        objective += sub.objective
        optimal = optimal and sub.optimal
        local_to_global: dict[int, int] = {}
        for node, local in sub.labels.items():
            if local not in local_to_global:
                local_to_global[local] = next_label
                next_label += 1
            labels[node] = local_to_global[local]

    return MulticutResult(labels=labels, objective=objective,
                          method=method, optimal=optimal)
