"""Shared Ollama client for Local AI."""
from __future__ import annotations

import json
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)


async def ollama_chat(url: str, model: str, messages: list[dict], **kwargs) -> str:
    """Send a chat request to Ollama and return the full response text via streaming."""
    payload = {"model": model, "messages": messages, "stream": True, **kwargs}
    _LOGGER.debug("Ollama request payload: %s", payload)
    text = []

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{url}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                if chunk := line.strip():
                    data = json.loads(chunk)
                    text.append(data.get("message", {}).get("content", ""))
                    if data.get("done"):
                        break

    return "".join(text)
