from pathlib import Path

from ..llm.base import LLMClient
from .store import VectorStore

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


async def load_knowledge_base(llm: LLMClient) -> VectorStore:
    store = VectorStore()
    for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        vector = await llm.embed(text)
        store.add(doc_id=path.stem, title=title, text=text, vector=vector)
    return store
