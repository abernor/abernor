"""PLAN phase — turn a natural-language goal into a concrete build plan."""

from __future__ import annotations

from ._llm import ask

_SYSTEM = (
    "You are the Planner in an autonomous build pipeline. Given a goal, produce a "
    "short, concrete implementation plan: the files to create, their responsibilities, "
    "and the acceptance criteria that TEST will check. Be specific and avoid filler."
)


def plan(goal: str) -> str:
    """Return an implementation plan for the given goal."""
    return ask(_SYSTEM, f"Goal:\n{goal}")
