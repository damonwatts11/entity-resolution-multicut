# Specification and definition of done

Project: entity resolution at scale by certified decomposition of the minimum cost multicut problem.

This file states when the project is finished. The project document describes what to build and why. This file only lists conditions that can be checked by running a command or opening a file. When the two disagree, the project document is corrected first and this file is updated in the same commit.

## 1. Principles

1. **Done means verifiable.** Every criterion below is checked by a command, a file or a number in a results file. A criterion that requires judgement is not a criterion.
2. **Done does not depend on the outcome of the hypotheses.** Each of H1 to H4 must be decided, with evidence. A refuted hypothesis, reported as such, satisfies the criterion.
3. **Two levels.** Level M (minimum) is the project that supports the thesis and may be listed on a CV. Level F (full) adds the incremental mode, the scaling study and the demonstration application. Level M must be complete before any Level F work is counted.
4. **No silent deviation.** Any departure from the project document is recorded in `DEVIATIONS.md` with its reason.

## 2. Scope

**In scope.** Synthetic generator, blocking, pairwise classifier, logit costs, kernel formation with cap B, completion, persistency reduction, greedy additive edge contraction, local search, integer program on small kernels, lower bounds, certificate (U, L, Δ, γ), baselines, metrics, experiments E1 to E6, incremental insertion, report, README, demonstration application.

**Out of scope.** Learned matchers beyond logistic regression, lifted multicuts, distributed engines such as Spark, deletion or modification of records, splitting rules based on minimum cuts, Kernighan-Lin with joins (optional, never required), any claim of commercial viability.

## 3. Interface that must exist

| Command | Effect |
| --- | --- |
| `make test` | Runs the whole test suite |
| `make reproduce-min` | Regenerates every Level M results file and figure from scratch |
| `make reproduce` | Regenerates every results file and figure of both levels |
| `make report` | Compiles the LaTeX report to `report/report.pdf` |
| `make app` | Launches the demonstration application (Level F) |

Results are written to `results/<experiment>.json` and figures to `figures/`. Figures are produced only from results files.

## 4. Level M: minimum project

Level M is done when every box in sections 4.1 to 4.6 is ticked.

### 4.1 Code and reproducibility

- [ ] The package installs in a fresh environment from a lock file or pinned requirements with one command.
- [ ] `make reproduce-min` completes without manual intervention on a clean clone.
- [ ] `make reproduce-min` completes in under 60 minutes on the development machine, whose description (processor, cores, memory) is stated in the README.
- [ ] Two consecutive runs of `make reproduce-min` produce results files that are identical apart from timing and memory fields.
- [ ] Every results file contains the configuration, the seed, the metrics, the certificate, the time per pipeline step, the peak memory and the commit hash.
- [ ] Solvers take a cost matrix and return labels. No solver imports the record, blocking or feature modules.

### 4.2 Correctness

- [ ] `make test` exits with status 0.
- [ ] Tests T1 to T19 and T22 of the project document are implemented, each identifiable by its id in the test name or docstring.
- [ ] Property tests T4, T5, T8, T12, T13 and T14 run on at least 500 random instances each.
- [ ] The brute-force solver is used as the reference in T4, T5, T8, T12 and T13.
- [ ] Line coverage of the modules `kernels`, `persistency`, `solvers`, `bounds` and `metrics` is at least 90%.
- [ ] On every Level M results file: L ≤ U, γ lies in [0, 1], every kernel size is at most B, and U equals the cost recomputed from the final labels to within 1e-6 relative error.
- [ ] The output partition of the pipeline refines the transitive closure partition on every Level M run (proposition 1).

### 4.3 Experiments

- [ ] E1 is run for n = 10^4 and 10^5 over the full (θ, ρ) grid with five seeds. Figure 1 exists.
- [ ] E2 is run at n = 10^5 over the full grid with five seeds. Figure 2 exists and shows the merge and split terms of the variation of information separately.
- [ ] E3 is run for B in {25, 50, 100, 200, 400, 800} at the two highest values of ρ. Figures 3 and 4 exist.
- [ ] E6 is run on Febrl 4 for every baseline and for certified decomposition. The table exists.
- [ ] All five baselines of the project document are implemented and appear in E2 and E6. Splink is not required.
- [ ] Every reported number is a mean over five seeds with its standard deviation.

### 4.4 Classifier and data hygiene

- [ ] Training, calibration and evaluation populations are generated with distinct seeds, and the code makes it impossible to pass the true partition to anything other than the evaluation module.
- [ ] The classifier is trained and calibrated on a sample that includes completion pairs.
- [ ] Two reliability diagrams exist, one on blocking pairs and one on completion pairs.
- [ ] Reduction ratio, pair completeness and the share of true non-matches among candidate pairs are reported for every configuration.

### 4.5 Hypotheses

- [ ] H1, H2 and H3 each receive one of three verdicts in the report: supported, refuted, or undecided with the reason.
- [ ] Each verdict cites the figure and the numbers on which it rests.
- [ ] The report states the cap B retained, the value of ret(B) at that cap, and the values of Δ and γ.

### 4.6 Report and README

- [ ] `make report` produces a PDF of eight to twelve pages, written in English, in LaTeX.
- [ ] The report contains: the problem statement, the four limits of the monolithic approach, the pipeline, propositions 1 to 3 with proofs, the lower bounds and the certificate, the experimental protocol, the figures of section 4.3, the verdicts of section 4.5, and a section on limitations.
- [ ] The limitations section states that the certificate refers to the completed instance, and which conclusions were observed on synthetic data only.
- [ ] The report makes no claim of commercial viability. It claims bounded memory per worker and a certified gap, at the population sizes actually run.
- [ ] Every reference has been checked against its source. No reference is cited from memory.
- [ ] The README states the problem in ten lines, shows one figure, gives the command that reproduces it, and links to the report.
- [ ] `DEVIATIONS.md` exists, even if empty.

## 5. Level F: full project

Level F is done when Level M is done and every box below is ticked.

### 5.1 Incremental mode

- [ ] Tests T20 and T21 are implemented and pass.
- [ ] E5 is run at n = 10^5 and 10^6. Figure 6 exists, with the median and the 99th percentile of insertion latency against B and against n.
- [ ] Identifier churn and the three drift quantities (variation of information, difference of U, difference of Δ) are reported in a table.
- [ ] H4 receives a verdict under the rules of section 4.5.

### 5.2 Scaling and second benchmark

- [ ] E1 is extended to n = 10^6.
- [ ] E4 is run with 1, 2, 4 and 8 workers. Figure 5 exists.
- [ ] Results are identical for every number of workers (test T17 at n = 10^5).
- [ ] Peak memory per worker is reported and compared with the bound of one B by B matrix.
- [ ] E6 is extended to one further public benchmark.

### 5.3 Demonstration application

- [ ] `make app` launches the application locally without further setup.
- [ ] The application imports the package and contains no resolution logic of its own.
- [ ] Controls: θ, ρ, B, seed, and n capped at 5,000.
- [ ] One view per pipeline step: records, candidate graph, kernels, one completed kernel drawn with positive and negative edges distinguished, final partition.
- [ ] A comparison view shows transitive closure and certified decomposition side by side, with the merge and split terms of the variation of information, the number of clusters, and U, L, Δ and γ.
- [ ] A change of any control updates every view in under 10 seconds at n = 5,000.
- [ ] Results at n = 10^5 and 10^6 are displayed from the saved results files and are not recomputed.
- [ ] The README embeds a screen recording of under one minute.

## 6. Explicitly not required

The project is done without any of the following: a confirmed hypothesis, a relative gap γ below any given value, a particular speed-up, a compiled solver, Kernighan-Lin with joins, Splink, the North Carolina voter data, or deployment of the application.

## 7. Review package

Before the project is submitted for review, the following are assembled:

1. The repository at the commit of the results.
2. The output of `make test`, with coverage.
3. The directory `results/` and the directory `figures/`.
4. The compiled report.
5. `DEVIATIONS.md`.
6. This file, with every box either ticked or annotated with the reason it is not.

## 8. Status

| Level | Boxes ticked | Date completed |
| --- | --- | --- |
| M | 0 of 33 | |
| F | 0 of 17 | |
