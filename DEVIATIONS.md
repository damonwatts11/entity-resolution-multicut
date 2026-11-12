# Deviations

Every departure from `docs/project.pdf` is recorded here with its reason, per
`CLAUDE.md`. If this file is empty, there are no deviations.

## Recorded

### D1. Project document kept as PDF, not Markdown

`CLAUDE.md` originally referenced `docs/project.md`. The canonical document is
the PDF "Entity resolution at scale by certified decomposition of the minimum
cost multicut problem", committed as `docs/project.pdf`. `CLAUDE.md` was
repointed to `docs/project.pdf` in the same commit.
**Reason:** no Markdown source of the document was available, and a
hand transcription of its propositions and formulas would risk altering the
mathematics that the tests check. **Effect:** the document is not diff-able or
greppable; changes to it must be described in commit messages.

### D2. Tables library: pandas

The document allows "polars or pandas". pandas was chosen.
**Reason:** broad wheel availability and tight integration with scikit-learn.
No behaviour depends on the choice.

### D3. Added tooling dependency: pytest-cov

Not listed in the `CLAUDE.md` dependency set. Added because `spec.md` 4.2
requires at least 90% line coverage on several modules, which needs a coverage
tool. It is a test-time tool only and is in the `dev` optional group.

### D4. streamlit is an optional extra

Listed in the `CLAUDE.md` dependency set, but placed in the `app` optional group
rather than the core dependencies. **Reason:** it is used only by the Level F
demonstration (`app/`); keeping it out of the core keeps the development
environment light. It is installed with `pip install -e ".[app]"`.
