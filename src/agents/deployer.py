"""DEPLOY phase — write generated code to the workspace so it can run.

This is a local, stub deployment: it persists the code to disk. Swap the body
for a real deploy target (container build, serverless push, etc.) later.
"""

from __future__ import annotations

from pathlib import Path

from ..config import settings


def deploy(code_text: str) -> Path:
    """Write the generated code to the workspace and return the artifact path."""
    workspace = settings.ensure_workspace()
    artifact = workspace / "generated.txt"
    artifact.write_text(code_text, encoding="utf-8")
    return artifact
