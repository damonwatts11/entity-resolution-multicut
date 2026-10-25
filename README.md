# Entity Resolution via Minimum-Cost Multicut

Reconciling client records across two systems (entity resolution), where the
pairwise matching decisions are mutually inconsistent.

## Approach
- Identify the records denoting the same entity when two reference datasets are reconciled.
- Formulate the partitioning as a **combinatorial optimization** problem
  (**minimum-cost multicut**), with the **transitivity constraint built into the
  model** rather than applied afterwards.
- Evaluated on synthetic data with a controlled corruption rate.

**Stack:** Python

## Why multicut?

Pairwise matchers score each record pair independently, so their verdicts are
often **intransitive**: A matches B, B matches C, but A does *not* match C. The
usual fix — threshold the scores and take the transitive closure — propagates
every spurious link, chaining unrelated records into bloated clusters.

The minimum-cost multicut avoids this by partitioning *globally*. Each record
pair becomes an edge with a signed weight (log-odds of being the same entity:
positive = "same", negative = "different"), and we choose the partition that
minimises the total weight of the **cut** edges, subject to **triangle
(transitivity) constraints**:

```
minimise   Σ  w_ij · x_ij          x_ij = 1  ⟺  edge i–j is cut
         i<j
s.t.       x_ij ≤ x_ik + x_kj      for all triples i, j, k   (transitivity)
           x_ij ∈ {0, 1}
```

The triangle inequalities forbid cutting exactly one edge of any triangle, so
the uncut edges always form a valid partition. Transitivity is a property of
the model's feasible region, not a post-processing step.

## Pipeline

```
records → pairwise scoring → signed edge weights → minimum-cost multicut → clusters
```

| Module | Role |
| --- | --- |
| `ermc.data` | Synthetic two-system generator with a controlled corruption rate (typos, dropped/reformatted fields). Carries ground-truth entity ids. |
| `ermc.similarity` | Fellegi–Sunter-style per-field comparison → match probability → signed log-odds edge weight. Blocking to prune candidate pairs. |
| `ermc.multicut` | The solver. Exact binary ILP with triangle constraints (PuLP + CBC), plus a greedy heuristic (GAEC). Decomposes into connected components so the exact solve scales. |
| `ermc.evaluate` | Pairwise precision/recall/F1 and Adjusted Rand Index (no scikit-learn). |
| `ermc.pipeline` | End-to-end glue. |

## Install

```bash
pip install -e .            # runtime (PuLP ships the CBC solver)
pip install -e ".[dev]"     # + pytest
```

Requires Python ≥ 3.10.

## Run the demo

```bash
python scripts/run_demo.py --entities 40 --corruption 0.3 --seed 7
```

It generates a synthetic instance, reconciles it with the exact multicut, and
compares against a naive *threshold + transitive-closure* baseline. On a harder
instance (200 entities, 40 % corruption) the difference is clear:

| Method | Precision | Recall | F1 | ARI |
| --- | --- | --- | --- | --- |
| **Minimum-cost multicut** | **0.49** | 0.75 | **0.59** | **0.59** |
| Threshold + transitive closure | 0.26 | 0.75 | 0.38 | 0.38 |

Same recall, but the baseline's transitive closure produces ~3× the false
positives by chaining records together; the multicut's built-in transitivity
keeps clusters tight. All 395 records are solved to proven optimality in ~1.5 s
thanks to component decomposition.

## Library use

```python
from ermc import generate_dataset, run_pipeline

ds = generate_dataset(n_entities=50, corruption_rate=0.3, seed=1)
result = run_pipeline(ds.records, truth=ds.truth(), method="auto")

print(result.multicut.method, result.multicut.optimal)
print(result.evaluation.summary())
print(result.labels)   # record_id -> predicted entity cluster
```

`method` is `"ilp"` (exact), `"gaec"` (fast greedy), or `"auto"` (exact per
component, greedy only for components too large to solve exactly).

## Tests

```bash
pytest
```

> Status: personal project (2026).
