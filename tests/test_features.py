"""Tests for ermc.features."""

from ermc import features


def test_featurize_exists():
    assert callable(features.featurize)
