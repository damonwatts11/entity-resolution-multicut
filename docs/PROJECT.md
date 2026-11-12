# Implementation plan: entity-resolution-multicut (certified decomposition)

## Context

The repo `damonwatts11/entity-resolution-multicut` was scaffolded this session: every `ermc/` module is a typed stub raising `NotImplementedError`, 16 smoke tests pass, and **0 of 50 spec boxes** (33 Level M + 17 Level F) are ticked. The work now is to implement the project from the stubs to a fully verifiable state, following the authority chain `docs/project.pdf` (behaviour) > `spec.md` (done) and the 8 invariants in `CLAUDE.md`.

This plan covers **both levels in full detail**. After approval it is handed to `/plan-to-ticket`, so it is organised as dependency-ordered, session-sized **work units** (U1 ... U19); each is a ticket candidate with explicit acceptance (T-tests + spec boxes) and dependencies. Unit numbers are a suggested ticket order.

## Guiding constraints (apply to every unit)

- **Test-first for anything a proposition specifies** (CLAUDE.md testing rules). Property tests use complete graphs with **integer** costs in `[-5, 5]`; brute force is the optimality reference; never weaken an assertion or widen a tolerance to pass.
- **Invariants:** solvers/persistency/bounds are pure (no `synth`/`blocking`/`features`/`model` import — already guarded by `tests/test_invariants.py`); true partition is evaluation-only; determinism (same seed and any worker count → identical output, ties by record index); single sign convention (positive = join; objective = sum of cut-edge costs); certificate `L <= U`, `γ ∈ [0,1]`, kernel `<= B`, `U` = cost recomputed from labels; output refines transitive closure; persistency contracts one edge at a time; figures read `results/*.json` only.
- **Record every departure** from `docs/project.pdf` in `DEVIATIONS.md` in the same commit.
- **Reuse the scaffold:** all module files and per-module test files already exist with the public signatures and the T-ids each test file owns (see `tests/test_*.py` docstrings). Fill them; do not restructure.

## Tech choices and reuse (validated against the installed env)

- **ILP:** `scipy.optimize.milp` (HiGHS) — confirmed importable. Triangle inequalities stated in full up to ~40 vertices, separated lazily beyond.
- **Graph ops:** `scipy.sparse.csgraph` (`connected_components`, `shortest_path`) for blocking components, refinement checks, kernel union and cycle separation. **No `networkx` dependency.**
- **Strings:** `rapidfuzz` (Jaro-Winkler, normalized Levenshtein). **Classifier:** `sklearn` `LogisticRegression` + `IsotonicRegression`/`CalibratedClassifierCV`.
- **Config format:** TOML via stdlib `tomllib` (no new dep). Replace `configs/example.yaml` with `configs/*.toml`.
- **Objective primitive:** add `cost(C, labels) -> float` to `ermc/solvers/__init__.py` (pure). Reused by `brute`, `bounds`, `moves`, `gaec` and `pipeline` (the `U` recompute). Record in `DEVIATIONS.md` (helper not in the original layout).

## Decisions to confirm (surfaced; defaults chosen)

1. **New dependency `recordlinkage`** — required for Level M (E6 loads the Febrl 4 data it distributes). This is the only new runtime dep. *Default: add it, record in `DEVIATIONS.md`.*
2. **MusicBrainz 20K** (Level F second benchmark, U18) — needs a small downloader/loader; licence to check. *Default: recommended benchmark per the doc; wire a cached loader.*
3. **Coverage gate** — add `--cov-fail-under=90` to `pyproject.toml` at U15, once the gated modules (`kernels`, `persistency`, `solvers`, `bounds`, `metrics`) are implemented.
4. **`recordlinkage` / MusicBrainz data** are fetched once and cached under a gitignored `data/` dir; never committed.

---

## Phase 0 — Pure core (integer-cost matrices, brute-force reference)

Everything here is matrix-in / labels-or-number-out, testable without the data layer.

### U1. Objective + brute-force solver — T1
- **Files:** `ermc/solvers/__init__.py` (`cost(C, labels)`), `ermc/solvers/brute.py`.
- **Do:** enumerate all set partitions up to 9 vertices; return min-cost labels; `cost` = sum of costs of cut edges under the sign convention.
- **Tests:** T1 (hand 4-vertex instance solved on paper); unit tests for `cost`.
- **Unlocks:** brute reference for 4.2; the `U`-recompute primitive (invariant 5).
- **Depends:** none.

### U2. Metrics — T18
- **Files:** `ermc/metrics.py` (`vi` → `(false_merges, false_splits)`, `pairwise`).
- **Tests:** T18 (identity, symmetry, relabelling, `{1,2},{3,4}` vs `{1,2,3,4}` = ln 2).
- **Unlocks:** part of 4.2; evaluation for all experiments.
- **Depends:** none.

### U3. GAEC + local search — T14
- **Files:** `ermc/solvers/gaec.py` (`solve`), `ermc/solvers/moves.py` (`improve`).
- **Do:** greedy additive edge contraction (O(s^3) dense form); vertex-move local search applied while gain < -1e-9; deterministic tie-break by index.
- **Tests:** T14 (cost never increases, search terminates); random-instance sanity vs brute.
- **Depends:** U1.

### U4. Exact ILP solver — T13
- **Files:** `ermc/solvers/ilp.py` (`solve(C, time_limit)` → `IlpResult`).
- **Do:** binary var per pair, triangle inequalities `x_ij <= x_ik + x_kj`; full set <=40 vertices, else lazy separation (solve, find violated triangles via `csgraph`, add, repeat); on time-out return GAEC labels + best proven lower bound.
- **Tests:** T13 (cost equals brute up to 8 vertices; no triangle inequality violated; property >=500).
- **Depends:** U1, U3.

### U5. Lower bounds — T12
- **Files:** `ermc/bounds.py` (`trivial_bound` = L_0, `cycle_packing_bound`, `lower_bound`).
- **Do:** L_0 = sum of negative costs; cycle packing over conflicted triangles (residual-weight accumulation).
- **Tests:** T12 (property: `L_0 <= L_pack <= OPT <= cost after local search <= cost after greedy`; OPT via brute).
- **Depends:** U1, U3, U4.

### U6. Persistency reduction — T5, T6, T7
- **Files:** `ermc/persistency.py` (`reduce(C)` → `(C_reduced, groups)`).
- **Do:** proposition 2 criterion at the cheapest instance `U = {u}`; **sequential** contraction (one edge, update matrix, re-test); never contract two edges sharing a vertex in one pass.
- **Tests:** T5 (optimum preserved, property >=500, brute ref), T6 (hand case incident costs 5, -2, 1 → edge of cost 5 contracted), T7 (contraction preserves partition cost).
- **Depends:** U1.

### U7. Kernel formation + completion — T8, T9, T10
- **Files:** `ermc/kernels.py` (`form_kernels(edges, B)` → members + `delta`), `ermc/completion.py` (`complete(kernel, edges, scorer)`).
- **Do:** Kruskal on positive edges by decreasing cost with a size cap `B` (capped union-find); abandoned positive edges sum to `Δ`. Completion fills known entries and scores the rest into a dense symmetric zero-diagonal matrix.
- **Tests:** T9 (sizes `<= B`, `Δ` = abandoned positive cost), T10 (no cap → components of G+ via `csgraph`, `Δ = 0`), T8 (proposition 3 property: regions, right − left = `Δ`; OPT via brute/ILP).
- **Depends:** U1, U4.

## Phase 1 — Data layer

### U8. Synthetic generator — (feeds T22, 4.4)
- **Files:** `ermc/synth.py` (`generate(n, theta, rho, seed)` → `Population`).
- **Do:** entities with attribute records; corruption model at character/token/field level scaled by `theta`; confusable density `rho` (households, group subsidiaries); stream order for incremental; three populations (train/calibrate/eval) with distinct seeds; true labels returned for evaluation only.
- **Tests:** determinism; coherent true labels; **4.4 hygiene** — distinct seeds and the type design makes it impossible to pass the true partition anywhere but `metrics`/training.
- **Depends:** none.

### U9. Blocking — (4.4 reporting)
- **Files:** `ermc/blocking.py` (`candidates`, `lookup`).
- **Do:** union of blocking keys (sorted neighbourhood on (family name, DOB) and (postal code, given name); inverted index on character 3-grams); report reduction ratio, pair completeness, share of true non-matches.
- **Tests:** reduction-ratio / pair-completeness / non-match-share on a known small population; `lookup` returns the right candidates for one record.
- **Depends:** U8.

### U10. Features + classifier + costs — T19
- **Files:** `ermc/features.py` (`featurize`), `ermc/model.py` (`CostModel.fit`, `.costs`).
- **Do:** features (Jaro-Winkler, normalized Levenshtein, token Jaccard, calendar distance, agreement + missingness indicators); logistic regression; isotonic calibration; clipped logit cost `c = log(p/(1-p))`, `p ∈ [eps, 1-eps]`, `eps = 1e-4`; sign flips at `p = 1/2`. Train/calibrate on a sample **including completion pairs**.
- **Tests:** T19 (`|c| <= log((1-eps)/eps)` for any feature vector); two reliability diagrams (blocking vs completion pairs) produced for 4.4.
- **Depends:** U8, U9.

### U11. Baselines — T2, T3, T11
- **Files:** `ermc/baselines.py` (`transitive_closure`, `thresholding`, `average_linkage`).
- **Do:** threshold at `p = 1/2` then components (`csgraph`); thresholding without closure; average linkage on `1 - p` inside G+ components.
- **Tests:** T2 (chain counterexample: `c_ab=2, c_bc=1, c_ac=-3` → closure `{a,b,c}`, multicut `{a,b},{c}` cost -2 — multicut side uses the solver), T3 (same with `ac` removed → `{a,b,c}` cost 0). Supports T11.
- **Depends:** U1 (solver for the multicut comparison in T2/T3), U8 for integration.

## Phase 2 — Integration

### U12. Pipeline + certificate (+ traces for the app) — T4, T11, T15, T16, T17, T22
- **Files:** `ermc/pipeline.py` (`resolve(records, B)` → `Resolution`; add an opt-in `traces` return of intermediates).
- **Do:** steps 1-7 (block, form kernels, complete, reduce, resolve = GAEC+moves, ILP when small, bound, assemble); parallel over kernels with a `multiprocessing` pool, deterministic and worker-count independent; certificate `U, L, Δ, γ`. Design the **traces** payload now (candidate graph, kernels, one completed kernel, final partition) so the Level F app reads it without re-running logic.
- **Tests:** T4 (prop 1 property, brute ref), T11 (B infinite + steps 3-6 off = transitive closure), T15 (`L<=U`, `γ∈[0,1]`, `U` = recomputed), T16 (all kernels ILP + `Δ=0` → `γ=0`), T17 (two seeds identical; 1 vs 4 workers identical labels + certificate), T22 (`theta=0, rho=0` every method recovers truth).
- **Unlocks:** invariants 2/3/5/6 on every run; most of 4.2.
- **Depends:** U1-U11.

## Phase 3 — Experiments, results, report (completes Level M)

### U13. Experiment harness + results schema
- **Files:** `ermc/experiments/run.py`, a results writer, `configs/*.toml`.
- **Do:** config-driven runs (parameters never in code); each run writes one JSON with config, seed, metrics, certificate (`U,L,Δ,γ`), time per pipeline step, peak memory (`tracemalloc`/`resource`), commit hash; 5 seeds, mean±std helper; deterministic across workers.
- **Unlocks:** 4.1 results-file-contents box; backbone for U14/U17/U18.
- **Depends:** U12.

### U14. Level M experiments E1, E2, E3, E6 + figures
- **Files:** `ermc/experiments/` scripts, `configs/`, figure builders, `results/`, `figures/`.
- **Do:** E1 (largest component share vs `rho`, n=10^4,10^5, full `(θ,ρ)` grid, Fig 1); E2 (VI vs `rho` at n=10^5, merge/split terms separate, Fig 2); E3 (B ∈ {25,50,100,200,400,800} at the two highest `rho`: ret(B), Δ, γ; kernel-size distribution + reduction rate, Figs 3-4); E6 (Febrl 4 via `recordlinkage`, all five baselines + certified decomposition, table). Figures from `results/*.json` only.
- **Tests/accept:** 4.3 boxes; every number mean±std over 5 seeds.
- **Depends:** U13, U11, (dep 1: `recordlinkage`).

### U15. Report + README + reproduce-min + coverage gate
- **Files:** `report/report.tex`, `README.md`, `Makefile`, `pyproject.toml`, `DEVIATIONS.md`.
- **Do:** fill the report (problem, 4 monolithic limits, pipeline, props 1-3 with proofs, bounds + certificate, protocol, Figs of 4.3, H1-H3 verdicts, limitations); verify every reference against its source; README (10-line problem, one figure, reproduce command, link to report, machine description); wire `make reproduce-min` to regenerate all Level M results+figures with no manual steps and < 60 min; pin a lock file; add `--cov-fail-under=90`; confirm two-run determinism; state H1/H2/H3 verdicts (supported/refuted/undecided) citing figures.
- **Accept:** all of 4.1, 4.5, 4.6; closes Level M (33/33).
- **Depends:** U14.

## Phase 4 — Level F

### U16. Incremental mode — T20, T21
- **Files:** `ermc/incremental.py` (`Resolver.insert`).
- **Do:** 8 steps of section 9.2 (candidates, touched kernels, region bounded by B, completion, resolution, safeguard vs trivial update, identifiers by maximum overlap, certificate); drift vs batch replay (section 9.4).
- **Tests:** T20 (post-insertion invariants: kernel `<=B`, records outside region keep identifier, running `U` = recomputed `U`), T21 (region cost `<=` trivial-update cost).
- **Accept:** 5.1 first box.
- **Depends:** U12.

### U17. E5 stream experiment + drift table
- **Files:** `ermc/experiments/` (E5), `configs/`, Fig 6.
- **Do:** replay stream at n=10^5 and 10^6; median and 99th-percentile insertion latency vs B and vs n (Fig 6); identifier churn + three drift quantities (VI, ΔU, ΔΔ) in a table; H4 verdict.
- **Accept:** remaining 5.1 boxes.
- **Depends:** U16, U13.

### U18. Scaling: E4 workers, E1→10^6, second benchmark
- **Files:** `ermc/experiments/` (E4), loaders, Fig 5.
- **Do:** E4 with 1,2,4,8 workers (Fig 5, speed-up; peak memory per worker vs the one-`B×B`-matrix bound; T17 at n=10^5 identical across workers); extend E1 to n=10^6; extend E6 to MusicBrainz 20K (dep 2 loader).
- **Accept:** 5.2 boxes.
- **Depends:** U12, U14.

### U19. Demonstration application
- **Files:** `app/app.py` (Streamlit; already a scaffold), README screen recording.
- **Do:** a pure-visualisation front end over the Python backend — it imports `ermc` and holds **no resolution logic of its own**. Controls θ, ρ, B, seed, n (<=5000); one view per pipeline step (records, candidate graph, kernels, one completed kernel with positive/negative edges distinguished, final partition) rendered from the U12 **traces**; a comparison view (transitive closure vs certified decomposition: VI merge/split terms, number of clusters, `U, L, Δ, γ`); any control change updates every view in < 10 s at n=5000; results at n=10^5/10^6 shown from saved `results/` files, not recomputed; embed a sub-one-minute screen recording in the README. Purpose: let a non-coder see end-to-end what the algorithm does and how it compares to the baseline.
- **Accept:** all of 5.3; closes Level F (17/17).
- **Depends:** U12 (traces), U14 (saved results).

---

## Suggested ticket order and dependency graph

```
U1 ─┬─ U3 ─┬─ U4 ─┬─ U5
    │       │      └─ U7 ─┐
    │       └─ U6 ───────┤
U2 ─┘                    │
U8 ─┬─ U9 ─ U10 ─────────┤
    └─ U11 ──────────────┤
                         U12 ─ U13 ─ U14 ─ U15   (Level M done)
                              └ U16 ─ U17
                                U18 (needs U14)
                                U19 (needs U12 traces + U14 results)
```
Critical path to the thesis minimum: **U1→U3→U4→U7→U12→U13→U14→U15**, with U2/U5/U6/U8-U11 as parallelisable prerequisites.

## Verification

- **Per unit:** `.venv/Scripts/python -m pytest -k T<id>` (and the whole suite) green; the unit's `spec.md` boxes become tickable (do not self-tick — report them).
- **Pure-core invariant:** `tests/test_invariants.py` stays green (no data-layer import leaks into solvers/persistency/bounds).
- **Level M gate:** `make reproduce-min` on a clean clone, no manual steps, < 60 min, run twice → results identical apart from timing/memory; coverage >=90% on the gated modules; `make report` → 8-12 page PDF; every Level M results file satisfies `L<=U`, `γ∈[0,1]`, kernel `<=B`, `U` = recomputed cost, and refinement.
- **Level F gate:** T20/T21 pass; E4 identical across worker counts (T17 at 10^5); `make app` launches and every control updates all views < 10 s at n=5000.
- **Note on tooling:** `make` is not installed on this machine; either install GNU Make or run the underlying commands (`.venv/Scripts/python -m pytest`, `... -m ermc.experiments.run ...`). Record in README.

## Spec coverage map (unit → boxes)

- 4.1 → U13 (results schema), U15 (install/reproduce/determinism); 4.2 → U1-U7, U12 (tests + invariants), U15 (coverage gate); 4.3 → U14; 4.4 → U8-U10; 4.5 → U15; 4.6 → U15.
- 5.1 → U16, U17; 5.2 → U18; 5.3 → U19.
