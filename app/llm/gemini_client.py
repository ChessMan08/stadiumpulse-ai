from typing import Any

import httpx

from .base import LLMError

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def build_generate_payload(prompt: str, system: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    return payload


def parse_generate_response(data: Any) -> str:
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected Gemini generate response: {data}") from exc


def parse_embed_response(data: Any) -> list[float]:
    try:
        return data["embedding"]["values"]
    except (KeyError, TypeError) as exc:
        raise LLMError(f"Unexpected Gemini embed response: {data}") from exc


class GeminiClient:
    def __init__(self, api_key: str, model: str, embed_model: str, timeout: float = 15.0) -> None:
        self._key = api_key
        self._model = model
        self._embed_model = embed_model
        self._http = httpx.AsyncClient(timeout=timeout)

    async def generate(self, prompt: str, system: str = "") -> str:
        url = f"{_BASE_URL}/{self._model}:generateContent?key={self._key}"
        resp = await self._http.post(url, json=build_generate_payload(prompt, system))
        resp.raise_for_status()
        return parse_generate_response(resp.json())

    async def embed(self, text: str) -> list[float]:
        url = f"{_BASE_URL}/{self._embed_model}:embedContent?key={self._key}"
        body = {"content": {"parts": [{"text": text}]}}
        resp = await self._http.post(url, json=body)
        resp.raise_for_status()
        return parse_embed_response(resp.json())

    async def aclose(self) -> None:
        await self._http.aclose()
