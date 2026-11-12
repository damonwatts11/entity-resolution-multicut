"""Scaffold smoke tests.

These check that the package and its public interface import cleanly. They are
not the T-numbered tests of the project document (section 11); those are added to
the per-module files as each module is implemented, with the test id in the name,
for example ``test_T5_persistency_preserves_optimum``.
"""

import importlib

import ermc


def test_version():
    assert isinstance(ermc.__version__, str)


def test_all_modules_import():
    modules = [
        "ermc.synth",
        "ermc.blocking",
        "ermc.features",
        "ermc.model",
        "ermc.kernels",
        "ermc.completion",
        "ermc.persistency",
        "ermc.bounds",
        "ermc.pipeline",
        "ermc.incremental",
        "ermc.baselines",
        "ermc.metrics",
        "ermc.solvers.gaec",
        "ermc.solvers.moves",
        "ermc.solvers.ilp",
        "ermc.solvers.brute",
    ]
    for name in modules:
        importlib.import_module(name)
