# Entity resolution at scale by certified decomposition of the minimum cost multicut problem

Entity resolution reconciles records that refer to the same real world entity
across two reference systems. The correct output is a partition of the records,
not a set of pairwise decisions, and the principled formulation of that step is
the minimum cost multicut problem, equivalent to correlation clustering.
The monolithic formulation does not operate at scale: the candidate graph holds
a giant component, it offers no incremental mode, and the exact solver returns
no distance to the optimum. This project implements **certified decomposition**,
which divides the instance into kernels of at most `B` records, completes,
reduces, solves and bounds each kernel independently, and returns a partition
together with an upper bound `U`, a lower bound `L`, the decomposition gap `Δ`
and the relative gap `γ`. It measures how much of the advantage of multicut over
thresholding plus transitive closure survives once every optimization problem is
size capped.

This is a research project with a falsifiable thesis, not a product. A refuted
hypothesis is a valid result.

## Status

Scaffold. Module and test files exist with their public interfaces and are not
yet implemented. No box of `spec.md` is ticked.

## Sources of truth

| File | Role |
| --- | --- |
| `docs/project.pdf` | What to build and why |
| `spec.md` | Definition of done: Level M and Level F checklists |
| `CLAUDE.md` | Working guidance and invariants |
| `DEVIATIONS.md` | Every departure from `docs/project.pdf`, with its reason |

## Layout

```
ermc/          package, one module per pipeline step
  solvers/     gaec, moves, ilp, brute (brute is for tests only)
  experiments/ one script per experiment, driven by a config file
tests/         one file per module, tests named after their id (T1 ... T22)
configs/       one file per experiment
results/       JSON only, written by experiments
figures/       produced only from results/
report/        LaTeX sources
app/           Streamlit demonstration (Level F)
```

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"         # add ",app" for the Level F demonstration
```

## Commands

| Command | Effect |
| --- | --- |
| `make test` | Full test suite with coverage |
| `make reproduce-min` | Regenerate every Level M results file and figure |
| `make reproduce` | Regenerate everything, both levels |
| `make report` | Compile `report/report.pdf` |
| `make app` | Launch the demonstration application (Level F) |

The development machine (processor, cores, memory) and the reproduction time are
to be stated here once Level M runs, per `spec.md` section 4.1.
