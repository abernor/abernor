"""AI Orchestrator entry point.

Usage:
    python main.py "Build a CLI that reverses a string"
"""

from __future__ import annotations

import sys

from src.orchestrator import run


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python main.py "<your goal>"')
        return 1

    goal = " ".join(sys.argv[1:])
    result = run(goal)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
