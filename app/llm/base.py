import logging
from typing import Protocol

logger = logging.getLogger("stadiumpulse.llm")


class LLMClient(Protocol):
    async def generate(self, prompt: str, system: str = "") -> str: ...

    async def embed(self, text: str) -> list[float]: ...


class LLMError(RuntimeError):
    pass


async def safe_generate(client: LLMClient, prompt: str, system: str, fallback: str) -> str:
    try:
        text = await client.generate(prompt, system=system)
        return text.strip() or fallback
    except Exception:
        logger.warning("LLM generate() failed, using deterministic fallback", exc_info=True)
        return fallback
