from ..llm.base import LLMClient, safe_generate
from ..rag.store import VectorStore
from ..schemas import OpsQueryResponse
from ..sensors.simulator import SensorSnapshot


def _alerts_payload(snapshot: SensorSnapshot) -> list[dict[str, object]]:
    return [
        {"gate": r.gate, "density": r.density, "anomaly": r.anomaly}
        for r in snapshot.alerts
    ]


async def diagnose(
    question: str,
    llm: LLMClient,
    store: VectorStore,
    snapshot: SensorSnapshot,
    language: str = "English",
) -> OpsQueryResponse:
    query_vector = await llm.embed(question)
    retrieved = store.search(query_vector, k=2)
    alerts = _alerts_payload(snapshot)

    facts = [f"- operator_question: {question}"]
    for doc in retrieved:
        facts.append(f"- sop[{doc.title}]: {doc.text.replace(chr(10), ' ')[:400]}")
    if alerts:
        for alert in alerts:
            facts.append(f"- live_alert: gate={alert['gate']} density={alert['density']} anomaly={alert['anomaly']}")
    else:
        facts.append("- live_alert: none, all gates nominal")

    system = (
        f"You are a stadium operations copilot. Using only the FACTS below, respond in "
        f"{language} with: the likely cause, severity (low/medium/high), and the recommended "
        f"action referencing the matching protocol. Keep it under 100 words."
    )
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Diagnose the situation now."

    if alerts:
        top = alerts[0]
        fallback = (
            f"Cause: {top['anomaly'] or 'elevated density'} at {top['gate']} gate "
            f"({top['density']} persons/sqm). See protocol: {retrieved[0].title if retrieved else 'n/a'}."
        )
    else:
        fallback = f"No active alerts. Reference protocol: {retrieved[0].title if retrieved else 'n/a'}."

    narrative = await safe_generate(llm, prompt, system, fallback)

    return OpsQueryResponse(
        question=question,
        retrieved_sops=[{"id": d.doc_id, "title": d.title} for d in retrieved],
        active_alerts=alerts,
        narrative=narrative,
    )
