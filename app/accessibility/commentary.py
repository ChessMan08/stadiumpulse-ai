from ..llm.base import LLMClient, safe_generate
from ..schemas import CommentaryResponse, Verbosity

DEMO_EVENTS: list[dict[str, object]] = [
    {
        "id": "e1", "minute": 1, "event_type": "kickoff",
        "team": None, "player": None, "detail": "Match begins at the centre circle.",
    },
    {
        "id": "e2", "minute": 17, "event_type": "corner",
        "team": "Home", "player": "Right winger",
        "detail": "Corner awarded on the right flank after a deflected clearance.",
    },
    {
        "id": "e3", "minute": 23, "event_type": "save",
        "team": "Away", "player": "Goalkeeper",
        "detail": "Diving save pushes the ball wide of the bottom left corner.",
    },
    {
        "id": "e4", "minute": 38, "event_type": "goal",
        "team": "Home", "player": "Striker",
        "detail": "Low first-time finish inside the box beats the goalkeeper.",
    },
    {
        "id": "e5", "minute": 45, "event_type": "half_time",
        "team": None, "player": None, "detail": "Half-time whistle.",
    },
    {
        "id": "e6", "minute": 57, "event_type": "foul",
        "team": "Away", "player": "Centre back",
        "detail": "Yellow card shown for a late challenge near the halfway line.",
    },
    {
        "id": "e7", "minute": 68, "event_type": "substitution",
        "team": "Home", "player": "Midfielder",
        "detail": "Fresh legs introduced in central midfield.",
    },
    {
        "id": "e8", "minute": 74, "event_type": "var_review",
        "team": "Away", "player": "Striker",
        "detail": "Goal disallowed after review for an offside position.",
    },
    {
        "id": "e9", "minute": 90, "event_type": "full_time",
        "team": None, "player": None, "detail": "Full-time whistle.",
    },
]

_EVENT_INDEX: dict[str, dict[str, object]] = {str(e["id"]): e for e in DEMO_EVENTS}


def get_event(event_id: str) -> dict[str, object]:
    event = _EVENT_INDEX.get(event_id)
    if event is None:
        raise KeyError(event_id)
    return event


async def generate_commentary(
    event: dict[str, object],
    llm: LLMClient,
    language: str = "English",
    verbosity: Verbosity = Verbosity.RICH,
) -> CommentaryResponse:
    style = "vivid and spatially descriptive, 2 sentences" if verbosity == Verbosity.RICH else "brief, 1 short sentence"
    system = (
        f"You are an audio-description commentator for blind and low-vision fans. Using only "
        f"the FACTS below, write in {language}, {style}. Do not invent facts not listed."
    )
    facts = [
        f"- minute: {event['minute']}",
        f"- event_type: {event['event_type']}",
        f"- team: {event['team'] or 'n/a'}",
        f"- player: {event['player'] or 'n/a'}",
        f"- detail: {event['detail']}",
    ]
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Narrate this moment now."
    fallback = f"Minute {event['minute']}: {event['detail']}"
    text = await safe_generate(llm, prompt, system, fallback)
    return CommentaryResponse(event_id=str(event["id"]), text=text)
