"""The orchestration loop: Plan -> Code -> Deploy -> Test -> Fix.

Drives the agents in sequence, retrying the Code/Deploy/Test/Fix cycle until the
tests pass or MAX_ITERATIONS is reached.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rich.console import Console

from . import agents
from .config import settings

console = Console()


@dataclass
class RunResult:
    goal: str
    plan: str
    code: str
    passed: bool
    iterations: int
    reports: list[str] = field(default_factory=list)


def run(goal: str) -> RunResult:
    """Execute the full pipeline for a goal and return the outcome."""
    console.rule("[bold]PLAN")
    plan_text = agents.plan(goal)
    console.print(plan_text)

    console.rule("[bold]CODE")
    code_text = agents.code(plan_text)
    console.print("[dim]…code generated[/dim]")

    reports: list[str] = []
    passed = False
    iteration = 0

    while iteration < settings.max_iterations:
        iteration += 1
        console.rule(f"[bold]DEPLOY (iteration {iteration})")
        artifact = agents.deploy(code_text)
        console.print(f"[dim]deployed to {artifact}[/dim]")

        console.rule(f"[bold]TEST (iteration {iteration})")
        result = agents.test(plan_text, code_text)
        reports.append(result.report)
        console.print(result.report)

        if result.passed:
            passed = True
            console.print("[bold green]All checks passed.[/bold green]")
            break

        console.rule(f"[bold]FIX (iteration {iteration})")
        code_text = agents.fix(plan_text, code_text, result.report)
        console.print("[dim]…code revised[/dim]")

    if not passed:
        console.print("[bold red]Gave up: max iterations reached.[/bold red]")

    return RunResult(
        goal=goal,
        plan=plan_text,
        code=code_text,
        passed=passed,
        iterations=iteration,
        reports=reports,
    )
