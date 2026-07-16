from ..llm.base import LLMClient, safe_generate
from .models import Shift, Volunteer


async def draft_briefing(volunteer: Volunteer, assigned_shifts: list[Shift], llm: LLMClient) -> str:
    language = next(iter(volunteer.languages), "English")
    shift_lines = [f"- shift: {s.gate} gate, {s.time_block}, role focus: {s.required_skill}" for s in assigned_shifts]
    system = (
        f"You are a volunteer coordinator. Using only the FACTS below, write a short, warm "
        f"briefing message in {language} for the volunteer. Keep it under 80 words."
    )
    facts = [f"- volunteer_name: {volunteer.name}"] + shift_lines
    if not assigned_shifts:
        facts.append("- note: no shifts currently assigned")
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Write the briefing now."

    if assigned_shifts:
        shift_summary = "; ".join(f"{s.gate} ({s.time_block})" for s in assigned_shifts)
        fallback = f"Hi {volunteer.name}, your shifts: {shift_summary}. Thank you for volunteering!"
    else:
        fallback = f"Hi {volunteer.name}, you have no shifts assigned yet. We'll follow up soon."

    return await safe_generate(llm, prompt, system, fallback)
