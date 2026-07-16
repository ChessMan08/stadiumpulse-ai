from ..llm.base import LLMClient, safe_generate
from ..schemas import FaqResponse

FAQS: dict[str, dict[str, str]] = {
    "lost_ticket": {
        "label": "Lost ticket",
        "fact": "Visit the box office at your entry gate with a valid photo ID to reissue a lost ticket.",
    },
    "gates_open": {
        "label": "When do gates open",
        "fact": "Gates open 2 hours before kickoff.",
    },
    "re_entry": {
        "label": "Re-entry policy",
        "fact": "Re-entry is not permitted once you exit the stadium footprint.",
    },
    "prohibited_items": {
        "label": "Prohibited items",
        "fact": "Outside food and drink, professional cameras, and any weapon are prohibited.",
    },
    "lost_and_found": {
        "label": "Lost and found",
        "fact": "Report lost items at the Fan Services desk near the South gate.",
    },
    "accessible_seating": {
        "label": "Accessible seating",
        "fact": (
            "Accessible seating and companion seats are available at every gate; "
            "ask any steward for the nearest accessible entrance."
        ),
    },
    "water_policy": {
        "label": "Water bottles",
        "fact": (
            "Empty reusable water bottles under 750 ml are allowed. "
            "Free water refill stations are located on every concourse level."
        ),
    },
    "wifi": {
        "label": "Stadium Wi-Fi",
        "fact": "Free Wi-Fi is available via the network 'FIFA2026-FanConnect'; no password required.",
    },
    "prayer_room": {
        "label": "Prayer and quiet room",
        "fact": (
            "Multi-faith prayer and quiet rooms are available near the East and West gates, "
            "open throughout the match day."
        ),
    },
    "first_aid": {
        "label": "First aid stations",
        "fact": (
            "First aid posts staffed by paramedics are located at every gate concourse "
            "and inside sections 110 and 240."
        ),
    },
    "child_policy": {
        "label": "Children and family",
        "fact": (
            "Children under 3 do not need a ticket but must sit on an adult's lap. "
            "Family-friendly areas with changing facilities are near the North gate."
        ),
    },
    "parking": {
        "label": "Stadium parking",
        "fact": (
            "Parking varies by venue; most FIFA 2026 stadiums use public transit and shuttle-based access. "
            "Check the Transit Assistant tab for your host city's parking policy."
        ),
    },
}


def list_topics() -> list[dict[str, str]]:
    return [{"id": topic_id, "label": v["label"]} for topic_id, v in FAQS.items()]


async def answer(topic_id: str, llm: LLMClient, language: str = "English") -> FaqResponse:
    topic = FAQS[topic_id]
    system = (
        f"You are a multilingual fan-services assistant. Using only the FACT below, answer "
        f"in {language}, one short sentence. Do not add information not listed."
    )
    prompt = f"FACTS:\n- answer: {topic['fact']}\n\nINSTRUCTION: Answer the fan's question now."
    text = await safe_generate(llm, prompt, system, fallback=topic["fact"])
    return FaqResponse(topic_id=topic_id, label=topic["label"], answer=text)
