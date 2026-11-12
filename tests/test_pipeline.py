"""Tests for ermc.pipeline.

Project document section 11 tests owned by this file:
    T4   proposition 1 (property): optimum of G equals sum of optima of the
         components of G+
    T11  limiting case: pipeline with B infinite and steps 3 to 6 disabled gives
         the transitive closure partition
    T15  certificate: L <= U, gamma in [0,1], U equals cost recomputed from labels
    T16  certificate, exact case: all kernels solved by ILP and Delta = 0 => gamma = 0
    T17  determinism: two runs with one seed, and runs with 1 and 4 workers, give
         identical labels and certificate
    T22  end to end, no noise: generator with theta = 0 and rho = 0, every method
         recovers the true partition
"""

from ermc import pipeline


def test_resolve_exists():
    assert callable(pipeline.resolve)
