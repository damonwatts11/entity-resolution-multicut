# Decisions

Append-only log of decisions taken while executing the project. Each entry has a
date, the decision, the reason, and the ticket it came from. Departures from
`docs/project.pdf` are also recorded in `DEVIATIONS.md`.

## 2026-11-12 — Project setup (from /project-to-tickets)

- **ILP via `scipy.optimize.milp` (HiGHS).** Open source, no licence, sufficient at kernel sizes. Supersedes an earlier Gurobi idea. From: planning.
- **No `networkx`; use `scipy.sparse.csgraph`.** `connected_components` / `shortest_path` cover blocking, refinement and cycle separation without a new dependency. From: planning.
- **Config format TOML via stdlib `tomllib`.** Avoids adding PyYAML; `configs/*.toml`. From: planning.
- **New runtime dependency `recordlinkage`.** Ships the Febrl 4 data required by Level M (E6). Also recorded in `DEVIATIONS.md`. From: planning.
- **Objective primitive `cost(C, labels)` lives in `ermc/solvers/__init__.py`.** Pure; reused by brute, bounds, moves, gaec and pipeline. Also recorded in `DEVIATIONS.md`. From: planning.
- **Issue tracking without custom labels or milestones.** The project is managed through the GitHub MCP, which cannot create labels or milestones. Milestone and work order are encoded in the ticket id `[M<n>-NN]` and in the epic checklist; type and status live in the ticket body (an open issue is pending, a closed issue is done). From: /project-to-tickets.
- **Merge policy: auto.** Each ticket session merges its own PR once the acceptance commands, code review and CI pass. From: /project-to-tickets.
