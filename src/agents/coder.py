"""CODE phase — implement the plan as source code."""

from __future__ import annotations

from ._llm import ask

_SYSTEM = (
    "You are the Coder in an autonomous build pipeline. Implement the given plan as "
    "complete, runnable code. Output each file as a fenced code block preceded by its "
    "path on its own line (e.g. `# path: app.py`). Write only what the plan requires."
)


def code(plan_text: str, *, model: str | None = None, effort: str | None = None) -> str:
    """Return generated source code for the given plan."""
    return ask(_SYSTEM, f"Plan:\n{plan_text}", model=model, effort=effort)
