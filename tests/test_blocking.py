"""Tests for ermc.blocking.

Reduction ratio, pair completeness and the share of true non-matches among
candidate pairs (spec.md 4.4) are checked here as they are implemented.
"""

from ermc import blocking


def test_blocking_exists():
    assert callable(blocking.candidates)
    assert callable(blocking.lookup)
