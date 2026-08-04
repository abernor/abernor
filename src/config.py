"""Central configuration and Claude client construction for the AI Orchestrator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from the environment (.env)."""

    model: str = os.getenv("ORCHESTRATOR_MODEL", "claude-opus-5")
    effort: str = os.getenv("ORCHESTRATOR_EFFORT", "high")
    workspace_dir: Path = Path(os.getenv("WORKSPACE_DIR", "./workspace"))
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "5"))

    def ensure_workspace(self) -> Path:
        """Create the workspace directory if it doesn't exist and return it."""
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        return self.workspace_dir


def build_client() -> anthropic.Anthropic:
    """Construct the Anthropic client.

    Credentials resolve from the environment (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN,
    or an `ant auth login` profile), so no key is passed explicitly.
    """
    return anthropic.Anthropic()


settings = Settings()
