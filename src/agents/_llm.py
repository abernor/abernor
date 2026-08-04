"""Shared helper for making a single Claude call from an agent."""

from __future__ import annotations

from ..config import build_client, settings

_client = build_client()


def ask(system: str, user: str) -> str:
    """Send one turn to Claude and return the concatenated text response.

    Adaptive thinking is enabled and effort comes from settings so each agent
    gets consistent reasoning behavior. Streaming keeps large outputs under the
    SDK's HTTP timeout.
    """
    with _client.messages.stream(
        model=settings.model,
        max_tokens=16000,
        system=system,
        thinking={"type": "adaptive"},
        output_config={"effort": settings.effort},
        messages=[{"role": "user", "content": user}],
    ) as stream:
        message = stream.get_final_message()

    return "".join(block.text for block in message.content if block.type == "text")
