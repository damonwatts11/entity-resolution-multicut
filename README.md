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

> Status: personal project (2026).
