"""TEST phase — evaluate the deployed code against the plan's acceptance criteria."""

from __future__ import annotations

from dataclasses import dataclass

from ._llm import ask

_SYSTEM = (
    "You are the Tester in an autonomous build pipeline. Given the plan and the code, "
    "decide whether the code satisfies the plan's acceptance criteria. Reply on the "
    "first line with exactly PASS or FAIL, then a brief explanation of any problems."
)


@dataclass
class TestResult:
    passed: bool
    report: str


def test(
    plan_text: str,
    code_text: str,
    *,
    model: str | None = None,
    effort: str | None = None,
) -> TestResult:
    """Return whether the code passes, plus a report describing any failures."""
    response = ask(
        _SYSTEM, f"Plan:\n{plan_text}\n\nCode:\n{code_text}", model=model, effort=effort
    )
    passed = response.strip().upper().startswith("PASS")
    return TestResult(passed=passed, report=response)
