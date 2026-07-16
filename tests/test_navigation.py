from app.navigation.venue_map import find_section
from app.navigation.wayfinder import wayfind
from app.schemas import AmenityType
from app.sensors.simulator import GateReading, SensorSnapshot


def test_find_section_matches_by_id():
    section = find_section("I'm in section 101, row 4")
    assert section.section_id == "101"


def test_find_section_matches_by_quadrant_keyword():
    section = find_section("sitting somewhere on the South side")
    assert section.quadrant == "South"


def test_find_section_falls_back_when_unmatched():
    section = find_section("no idea where I am")
    assert section.section_id


async def test_wayfind_returns_requested_amenity(mock_llm):
    result = await wayfind("101", AmenityType.RESTROOM, mock_llm)
    assert "Restroom" in result.destination
    assert result.amenity == AmenityType.RESTROOM
    assert result.walk_minutes > 0


async def test_wayfind_flags_congestion_at_nearest_gate(mock_llm):
    congested = SensorSnapshot(
        timestamp=0.0,
        readings=[GateReading("North", density=4.2, temperature_c=22.0, air_quality_index=50)],
    )
    result = await wayfind("101", AmenityType.GATE, mock_llm, snapshot=congested)
    assert result.congestion_warning is not None
