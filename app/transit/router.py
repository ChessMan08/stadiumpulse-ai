from ..llm.base import LLMClient, safe_generate
from ..schemas import TransitRouteResponse
from ..sensors.simulator import DENSITY_ALERT_THRESHOLD, SensorSnapshot
from .data import CITIES, City, Zone, match_zone


def _congestion_warning(gate: str, snapshot: SensorSnapshot | None) -> tuple[str, str | None]:
    if snapshot is None:
        return gate, None
    reading = next((r for r in snapshot.readings if r.gate == gate), None)
    if reading and reading.density >= DENSITY_ALERT_THRESHOLD:
        alternative = min(snapshot.readings, key=lambda r: r.density)
        warning = f"{gate} gate is congested ({reading.density} persons/sqm); rerouted to {alternative.gate} gate."
        return alternative.gate, warning
    return gate, None


def _build_prompt(
    city: City, zone: Zone, gate: str, minutes: int, warning: str | None, language: str,
) -> tuple[str, str]:
    system = (
        "You are a multilingual stadium transit assistant. Using only the FACTS below, "
        f"write 2-3 short, friendly sentences in {language} guiding a fan to the stadium. "
        "Do not invent facts not listed."
    )
    facts = [
        f"- stadium: {city.stadium}",
        f"- departure_zone: {zone.name}",
        f"- transport_modes: {' then '.join(zone.mode_sequence)}",
        f"- estimated_minutes: {minutes}",
        f"- recommended_gate: {gate}",
        f"- parking_policy: {city.parking_policy}",
    ]
    if city.disruption:
        facts.append(f"- service_disruption: {city.disruption}")
    if warning:
        facts.append(f"- congestion_warning: {warning}")
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Write the guidance now."
    return prompt, system


async def build_route(
    city_id: str,
    origin_text: str,
    llm: LLMClient,
    snapshot: SensorSnapshot | None = None,
    language: str = "English",
) -> TransitRouteResponse:
    city = CITIES[city_id]
    zone = match_zone(city, origin_text)
    minutes = zone.base_minutes + (10 if city.disruption else 0)
    gate, warning = _congestion_warning(zone.gate, snapshot)

    prompt, system = _build_prompt(city, zone, gate, minutes, warning, language)
    fallback = (
        f"Take {' then '.join(zone.mode_sequence)} from {zone.name} to {city.stadium} "
        f"(about {minutes} min). Use {gate} gate."
        + (f" Note: {warning}" if warning else "")
    )
    narrative = await safe_generate(llm, prompt, system, fallback)

    return TransitRouteResponse(
        city=city.label,
        stadium=city.stadium,
        zone=zone.name,
        modes=list(zone.mode_sequence),
        estimated_minutes=minutes,
        recommended_gate=gate,
        congestion_warning=warning,
        narrative=narrative,
    )


def list_cities() -> list[dict[str, str]]:
    return [{"id": c.city_id, "label": c.label, "stadium": c.stadium} for c in CITIES.values()]
