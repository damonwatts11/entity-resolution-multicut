# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Entity resolution between two customer reference systems, formulated as a minimum cost multicut problem and solved by **certified decomposition**: the instance is divided into kernels of at most `B` records, each kernel is completed, reduced, solved and bounded independently, and the pipeline returns a partition together with an upper bound `U`, a lower bound `L`, the decomposition gap `Δ` and the relative gap `γ`.

This is a research project with a falsifiable thesis, not a product. A refuted hypothesis is a valid result. Never tune code, data or thresholds to make a hypothesis come out as supported.

## Sources of truth

Read these before any non-trivial change. Do not restate their content here.

| File | Role |
| --- | --- |
| `docs/project.pdf` | What to build and why: formulation, propositions 1 to 3, algorithms (section 8), incremental mode (section 9), tests T1 to T22 (section 11), experiments E1 to E6 and hypotheses H1 to H4 (section 12) |
| `spec.md` | Definition of done: Level M and Level F checklists |
| `docs/PROJECT.md` | Implementation plan: the work units (U1 to U19) and milestones the tickets map to |
| `docs/DECISIONS.md` | Append-only log of execution decisions |
| `DEVIATIONS.md` | Every departure from `docs/project.pdf`, with its reason |

Order of authority: `docs/project.pdf` defines behaviour, `spec.md` defines completion. If the two disagree, stop and ask. If an implementation must depart from `docs/project.pdf`, record it in `DEVIATIONS.md` in the same commit.

## Commands

| Command | Effect |
| --- | --- |
| `make test` | Full test suite with coverage |
| `make reproduce-min` | Regenerates every Level M results file and figure |
| `make reproduce` | Regenerates everything, both levels |
| `make report` | Compiles `report/report.pdf` |
| `make app` | Launches the demonstration application |

Single test: `pytest tests/test_persistency.py -k T5`. If a command in this table does not exist yet, creating it is part of the work, with exactly this name.

## Layout

```
ermc/
  synth.py          generator, corruption model, confusable entities, stream order
  blocking.py       candidate pairs, index lookup
  features.py       similarity features for a batch of pairs
  model.py          logistic regression, calibration, clipped logit costs
  kernels.py        capped union (section 8.1), returns kernels and Δ
  completion.py     dense cost matrix of a kernel
  persistency.py    reduction (section 8.3)
  solvers/          gaec.py, moves.py, ilp.py, brute.py (tests only)
  bounds.py         trivial and cycle packing lower bounds
  pipeline.py       steps 1 to 7, parallel over kernels, certificate
  incremental.py    state and insertion (section 9)
  baselines.py      transitive closure, thresholding, average linkage
  metrics.py        variation of information, pairwise scores
  experiments/      one script per experiment, driven by a config file
tests/              one file per module, tests named after their id (T1 ... T22)
configs/            one file per experiment
results/            JSON only, written by experiments
figures/            produced only from results/
report/             LaTeX sources
app/                Streamlit demonstration, no resolution logic of its own
```

`ermc` is a placeholder name. If it is renamed, rename it everywhere in one commit.

## Invariants

These hold at all times. A change that breaks one is wrong, whatever the tests say.

1. **Solvers are pure.** Functions in `solvers/`, `persistency.py` and `bounds.py` take a cost matrix and return labels or numbers. They never import `synth`, `blocking`, `features` or `model`.
2. **The true partition is evaluation-only.** Ground truth labels are passed to `metrics` and to classifier training on the dedicated training population, and to nothing else. No pipeline step may read them.
3. **Determinism.** Same seed, same output. Ties are broken by record index. Results are identical for any number of workers. No use of unseeded randomness, set iteration order or wall-clock time in any decision.
4. **Sign convention.** Positive cost favours joining, negative favours cutting. The objective is the sum of the costs of cut edges. Do not introduce a second convention anywhere.
5. **Certificate consistency.** `L <= U`, `γ` in `[0, 1]`, every kernel has at most `B` records, and `U` equals the cost recomputed from the final labels.
6. **Refinement.** The output partition refines the transitive closure partition.
7. **Persistency is sequential.** Contract one edge, update the matrix, test again. Never contract several edges that share a vertex from one evaluation of the criterion.
8. **Figures come from files.** Plotting code reads `results/*.json` only.

## Conventions

- Python 3.11 or later. Type hints on every public function. Docstrings state shapes and dtypes of arrays.
- Records are indexed `0 .. |V|-1`. Edges are three aligned arrays `(u, v, c)` with `u < v`, `int32` and `float32`. A partition is one `int` array of labels.
- A kernel is an array of record indices plus a dense symmetric cost matrix with zero diagonal.
- Write the numpy version first. Use numba only after profiling shows a hotspot, and keep both versions under the same tests.
- No new dependency without asking. Current set: numpy, scipy, scikit-learn, rapidfuzz, polars or pandas, pytest, hypothesis, matplotlib, streamlit.
- Prose in the report, README and docstrings: formal register, no em-dashes.

## Testing rules

- Every test in section 11 of `docs/project.pdf` carries its id in its name, for example `test_T5_persistency_preserves_optimum`.
- Random instances in property tests are complete graphs with **integer** costs in `[-5, 5]`, so that cost comparisons are exact.
- The brute-force solver is the reference for optimality. Never weaken an assertion or widen a tolerance to make a test pass. If a test from the project document fails, the code is presumed wrong. If you believe the test or the mathematics is wrong, stop and explain with a minimal counterexample.
- Write the test before the implementation when the behaviour is specified by a proposition.
- Do not delete, skip or mark as expected failure any T-numbered test without explicit approval.

## Experiments

- Each experiment is a config file plus a script. Parameters never live in code.
- Each run writes one JSON file with: configuration, seed, metrics, certificate (`U`, `L`, `Δ`, `γ`), time per pipeline step, peak memory, commit hash.
- Five seeds per configuration. Report mean and standard deviation.
- Long runs (n = 10^5 and above) are launched only when asked. Develop and debug at n = 10^3 to 10^4.

## Out of scope

Do not implement or propose unless asked: learned matchers beyond logistic regression, lifted multicuts, distributed engines, deletion or modification of records, minimum-cut splitting rules. Kernighan-Lin with joins is optional and never blocks anything.

## Working method

1. At the start of a session, read `spec.md` and `DEVIATIONS.md`, then run `make test` to establish the current state.
2. Work on one unit at a time: one module, one test group or one experiment. Keep changes small enough to review.
3. Before declaring a task finished, run `make test` and state which boxes of `spec.md` the change allows to be ticked. Do not tick boxes yourself.
4. Report results as they are. If an experiment contradicts a hypothesis, say so plainly and do not adjust the setup to change the outcome.
5. When something in the project document is ambiguous or appears incorrect, ask before choosing an interpretation.

## Ticket workflow

Execution is planned as GitHub issues (see the epic). Work them with the
work-ticket skill, one ticket per fresh conversation, one branch and one PR per
issue, code review before the PR, and a `## Handoff` comment on the issue at the
end. Append one line to the epic `## Progress` section when a ticket finishes.

- **Tracking without custom labels.** This repo is managed through the GitHub MCP,
  which cannot create labels or milestones. Milestone and order are in the ticket
  id `[M<n>-NN]` and the epic checklist; type and status are in the ticket body.
  An open issue is pending, a closed issue is done.
- **Merge policy: auto.** Each ticket session merges its own PR once the
  acceptance commands, the review and CI pass.
- **Working rules.** Never expand a ticket's scope. No invented results: every
  number comes from a reproducible script. For local, reversible details, assume
  and document in the handoff; for anything that changes the spec or another
  ticket, ask or block.
