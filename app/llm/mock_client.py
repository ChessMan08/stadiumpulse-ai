import hashlib
import re

_EMBED_DIM = 256
_FACTS_RE = re.compile(r"^-\s*([\w ]+):\s*(.+)$", re.MULTILINE)


class MockLLMClient:
    async def generate(self, prompt: str, system: str = "") -> str:
        facts = _FACTS_RE.findall(prompt)
        if not facts:
            return "No additional context available in demo mode."
        parts = [f"{k.strip()}: {v.strip()}" for k, v in facts]
        return "; ".join(parts) + ". (demo mode — add GEMINI_API_KEY for natural-language output)"

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * _EMBED_DIM
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % _EMBED_DIM  # noqa: S324
            vector[idx] += 1.0
        norm = sum(v * v for v in vector) ** 0.5
        return [v / norm for v in vector] if norm else vector
