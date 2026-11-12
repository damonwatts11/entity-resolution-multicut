"""Tests for ermc.synth.

No T-numbered test is assigned to the generator directly; its correctness is
exercised end to end by T22 (see test_pipeline.py). Data-hygiene checks of
spec.md 4.4 (distinct seeds, true partition reaches evaluation only) are added
here as they are implemented.
"""

from ermc import synth


def test_generate_exists():
    assert callable(synth.generate)
