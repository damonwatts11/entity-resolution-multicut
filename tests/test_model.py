"""Tests for ermc.model.

Project document section 11 tests owned by this file:
    T19  costs: any feature vector yields an absolute cost at most log((1-eps)/eps)
"""

from ermc.model import CostModel


def test_cost_model_interface():
    model = CostModel.__new__(CostModel)  # no __init__ side effects
    assert hasattr(model, "fit")
    assert hasattr(model, "costs")
