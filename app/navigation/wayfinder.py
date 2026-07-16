from ..llm.base import LLMClient, safe_generate
from ..schemas import AmenityType, WayfindResponse
from ..sensors.simulator import DENSITY_ALERT_THRESHOLD, SensorSnapshot
from .venue_map import Section, find_section


def _congestion_check(section: Section, snapshot: SensorSnapshot | None) -> str | None:
    if snapshot is None:
        return None
    reading = next((r for r in snapshot.readings if r.gate == section.nearest_gate), None)
    if reading and reading.density >= DENSITY_ALERT_THRESHOLD:
        return f"{section.nearest_gate} gate concourse is busy ({reading.density} persons/sqm); allow extra time."
    return None


async def wayfind(
    section_query: str,
    amenity: AmenityType,
    llm: LLMClient,
    snapshot: SensorSnapshot | None = None,
    language: str = "English",
) -> WayfindResponse:
    section = find_section(section_query)
    destination = section.destination(amenity)
    warning = _congestion_check(section, snapshot)

    facts = [
        f"- section: {section.section_id} ({section.level} level, {section.quadrant} quadrant)",
        f"- destination: {destination}",
        f"- walk_minutes: {section.walk_minutes}",
    ]
    if warning:
        facts.append(f"- congestion_warning: {warning}")
    system = (
        f"You are an in-stadium wayfinding assistant. Using only the FACTS below, give 1-2 "
        f"short walking directions in {language}. Do not invent facts not listed."
    )
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Give directions now."
    fallback = f"From section {section.section_id}, head to {destination} (about {section.walk_minutes} min walk)."
    if warning:
        fallback += f" Note: {warning}"

    narrative = await safe_generate(llm, prompt, system, fallback)

    return WayfindResponse(
        section=section.section_id,
        quadrant=section.quadrant,
        amenity=amenity,
        destination=destination,
        walk_minutes=section.walk_minutes,
        congestion_warning=warning,
        narrative=narrative,
    )
