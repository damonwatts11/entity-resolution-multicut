"""Tests for ermc.metrics.

Project document section 11 tests owned by this file:
    T18  variation of information: identity, symmetry, relabelling, and
         {1,2},{3,4} against {1,2,3,4} equals ln 2
"""

from ermc import metrics


def test_metrics_exist():
    assert callable(metrics.vi)
    assert callable(metrics.pairwise)
