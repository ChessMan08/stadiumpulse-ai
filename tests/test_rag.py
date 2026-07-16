from app.llm.mock_client import MockLLMClient
from app.rag.store import VectorStore

CROWD_TEXT = "Crowd density turnstile gate congestion queue steward redirect"
MEDICAL_TEXT = "Medical emergency ambulance collapse breathing injury paramedic"


async def _build_store() -> VectorStore:
    llm = MockLLMClient()
    store = VectorStore()
    store.add("crowd", "Crowd Control", CROWD_TEXT, await llm.embed(CROWD_TEXT))
    store.add("medical", "Medical Emergency", MEDICAL_TEXT, await llm.embed(MEDICAL_TEXT))
    return store


async def test_retrieval_favors_matching_topic():
    llm = MockLLMClient()
    store = await _build_store()

    query_vector = await llm.embed("The turnstile is jammed and the gate queue is congested")
    top = store.search(query_vector, k=1)[0]
    assert top.doc_id == "crowd"

    query_vector = await llm.embed("A fan collapsed and needs a paramedic urgently")
    top = store.search(query_vector, k=1)[0]
    assert top.doc_id == "medical"


async def test_search_on_empty_store_returns_empty_list():
    store = VectorStore()
    assert store.search([0.1, 0.2], k=2) == []
