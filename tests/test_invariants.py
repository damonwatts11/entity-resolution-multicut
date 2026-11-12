"""Structural guards for the CLAUDE.md invariants that can be checked statically.

Invariant 1: the pure modules (solvers, persistency, bounds) must not import
synth, blocking, features or model. This is checked by parsing their source, so
it holds even before the modules are implemented.
"""

import ast
import importlib.util
import pathlib

PURE_MODULES = [
    "ermc.persistency",
    "ermc.bounds",
    "ermc.solvers.gaec",
    "ermc.solvers.moves",
    "ermc.solvers.ilp",
    "ermc.solvers.brute",
]

FORBIDDEN = {"synth", "blocking", "features", "model"}


def _imported_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            # e.g. "from ermc.synth import X" -> last component "synth"
            names.add(node.module.rsplit(".", 1)[-1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.rsplit(".", 1)[-1])
    return names


def test_pure_modules_do_not_import_data_layer():
    for module in PURE_MODULES:
        spec = importlib.util.find_spec(module)
        assert spec is not None and spec.origin is not None
        imported = _imported_names(pathlib.Path(spec.origin))
        leaked = imported & FORBIDDEN
        assert not leaked, f"{module} imports forbidden modules: {sorted(leaked)}"
