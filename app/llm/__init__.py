from ..config import Settings
from .base import LLMClient, LLMError, safe_generate
from .gemini_client import GeminiClient
from .mock_client import MockLLMClient


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.active_llm_provider == "gemini":
        return GeminiClient(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            embed_model=settings.gemini_embed_model,
        )
    return MockLLMClient()


__all__ = ["LLMClient", "LLMError", "safe_generate", "build_llm_client", "GeminiClient", "MockLLMClient"]
