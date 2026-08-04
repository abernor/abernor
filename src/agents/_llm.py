"""Shared helper for making a single Claude call from an agent."""

from __future__ import annotations

from ..config import build_client, settings

_client = build_client()


def ask(
    system: str,
    user: str,
    *,
    model: str | None = None,
    effort: str | None = None,
) -> str:
    """Send one turn to Claude and return the concatenated text response.

    Adaptive thinking is enabled. ``model`` and ``effort`` default to the values
    in settings, but callers (e.g. the web UI) can override them per run without
    mutating global config. Streaming keeps large outputs under the SDK's HTTP
    timeout.
    """
    with _client.messages.stream(
        model=model or settings.model,
        max_tokens=16000,
        system=system,
        thinking={"type": "adaptive"},
        output_config={"effort": effort or settings.effort},
        messages=[{"role": "user", "content": user}],
    ) as stream:
        message = stream.get_final_message()

    return "".join(block.text for block in message.content if block.type == "text")
