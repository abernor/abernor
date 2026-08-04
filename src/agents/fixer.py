"""FIX phase — repair the code using the failing test report."""

from __future__ import annotations

from ._llm import ask

_SYSTEM = (
    "You are the Fixer in an autonomous build pipeline. Given the plan, the current "
    "code, and a failing test report, produce corrected code. Output the same "
    "path-annotated fenced-code-block format as the Coder. Change only what is needed "
    "to make the tests pass."
)


def fix(plan_text: str, code_text: str, report: str) -> str:
    """Return corrected code addressing the failing test report."""
    user = f"Plan:\n{plan_text}\n\nCurrent code:\n{code_text}\n\nTest report:\n{report}"
    return ask(_SYSTEM, user)
