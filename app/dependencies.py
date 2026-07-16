from typing import Any

from fastapi import Request

from .llm.base import LLMClient
from .rag.store import VectorStore
from .sensors.simulator import SensorSimulator


def get_llm(request: Request) -> LLMClient:
    return request.app.state.llm


def get_store(request: Request) -> VectorStore:
    return request.app.state.store


def get_sensors(request: Request) -> SensorSimulator:
    return request.app.state.sensors


def get_workforce_cache(request: Request) -> dict[str, Any]:
    return request.app.state.workforce_cache
