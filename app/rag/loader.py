import logging
from pathlib import Path

from ..llm.base import LLMClient
from ..llm.mock_client import MockLLMClient
from .store import VectorStore

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
logger = logging.getLogger("stadiumpulse")


async def load_knowledge_base(llm: LLMClient) -> VectorStore:
    store = VectorStore()
    fallback = MockLLMClient()
    for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        try:
            vector = await llm.embed(text)
        except Exception:
            logger.warning("Embed failed for %s, using fallback", path.stem)
            vector = await fallback.embed(text)
        store.add(doc_id=path.stem, title=title, text=text, vector=vector)
    return store
