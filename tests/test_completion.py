"""Tests for ermc.completion."""

from ermc import completion


def test_complete_exists():
    assert callable(completion.complete)
