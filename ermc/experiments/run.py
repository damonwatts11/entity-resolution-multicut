"""Experiment runner entry point (used by ``make reproduce-min`` / ``make reproduce``).

Usage:
    python -m ermc.experiments.run --level {min,full}

Currently a scaffold: the experiment scripts (E1 to E6) are not implemented yet.
When implemented, each experiment reads its config from ``configs/`` and writes
one JSON file per run to ``results/``, from which the figures are built.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate results and figures.")
    parser.add_argument(
        "--level",
        choices=["min", "full"],
        required=True,
        help="'min' for Level M experiments, 'full' for both levels.",
    )
    args = parser.parse_args(argv)
    print(
        f"[ermc] Experiment runner is a scaffold; level '{args.level}' is not "
        "implemented yet. See spec.md section 4.3 and docs/project.pdf section 12.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
