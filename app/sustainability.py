from dataclasses import dataclass

from .llm.base import LLMClient, safe_generate
from .sensors.simulator import SensorSnapshot

BASELINE_KW_PER_ZONE = 40.0
COMFORT_DENSITY = 2.0
TEMP_SETPOINT_C = 22.0
DENSITY_LOAD_COEFFICIENT = 12.0
TEMP_LOAD_COEFFICIENT = 3.0
REDUCIBLE_DENSITY_THRESHOLD = 1.0
REDUCIBLE_SAVINGS_FRACTION = 0.15


@dataclass
class ZoneEstimate:
    gate: str
    estimated_kw: float
    reducible: bool
    potential_savings_kw: float


@dataclass
class SustainabilityReport:
    zones: list[ZoneEstimate]
    total_estimated_kw: float
    total_potential_savings_kw: float
    reducible_zones: list[str]
    tip: str


def _estimate_zone(gate: str, density: float, temperature_c: float) -> ZoneEstimate:
    occupancy_load = max(0.0, density - COMFORT_DENSITY) * DENSITY_LOAD_COEFFICIENT
    temp_load = abs(temperature_c - TEMP_SETPOINT_C) * TEMP_LOAD_COEFFICIENT
    estimated_kw = round(BASELINE_KW_PER_ZONE + occupancy_load + temp_load, 1)

    reducible = density < REDUCIBLE_DENSITY_THRESHOLD
    savings = round(BASELINE_KW_PER_ZONE * REDUCIBLE_SAVINGS_FRACTION, 1) if reducible else 0.0

    return ZoneEstimate(gate=gate, estimated_kw=estimated_kw, reducible=reducible, potential_savings_kw=savings)


def compute_zones(snapshot: SensorSnapshot) -> list[ZoneEstimate]:
    return [_estimate_zone(r.gate, r.density, r.temperature_c) for r in snapshot.readings]


async def build_report(snapshot: SensorSnapshot, llm: LLMClient, language: str = "English") -> SustainabilityReport:
    zones = compute_zones(snapshot)
    total_kw = round(sum(z.estimated_kw for z in zones), 1)
    total_savings = round(sum(z.potential_savings_kw for z in zones), 1)
    reducible_zones = [z.gate for z in zones if z.reducible]

    facts = [
        f"- total_estimated_kw: {total_kw}",
        f"- reducible_zones: {', '.join(reducible_zones) or 'none'}",
        f"- potential_savings_kw: {total_savings}",
    ]
    system = (
        "You are a stadium sustainability engineer. Using only the FACTS below, give one "
        f"short, concrete HVAC or lighting adjustment recommendation in {language}, under 30 words."
    )
    prompt = "FACTS:\n" + "\n".join(facts) + "\n\nINSTRUCTION: Give the recommendation now."
    if reducible_zones:
        fallback = (
            f"Reduce HVAC/lighting at {', '.join(reducible_zones)}; "
            f"low occupancy allows {total_savings} kW savings."
        )
    else:
        fallback = "All zones at comfortable occupancy; maintain standard HVAC and lighting schedule."

    tip = await safe_generate(llm, prompt, system, fallback)

    return SustainabilityReport(
        zones=zones,
        total_estimated_kw=total_kw,
        total_potential_savings_kw=total_savings,
        reducible_zones=reducible_zones,
        tip=tip,
    )
