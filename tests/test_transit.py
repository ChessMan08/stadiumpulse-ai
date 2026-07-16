from app.transit.router import build_route


async def test_route_matches_zone_by_keyword(mock_llm):
    result = await build_route("dallas", "I'm staying near the DFW airport", mock_llm)
    assert "DFW" in result.zone or "CentrePort" in result.zone
    assert result.stadium == "AT&T Stadium"
    assert result.estimated_minutes > 0


async def test_route_falls_back_to_default_zone_when_unmatched(mock_llm):
    result = await build_route("miami", "somewhere unrecognized", mock_llm)
    assert result.zone == "Downtown Miami"


async def test_route_reroutes_on_gate_congestion(mock_llm, congested_snapshot):
    result = await build_route("miami", "downtown", mock_llm, snapshot=congested_snapshot)
    assert result.recommended_gate != "North"
    assert result.congestion_warning is not None


async def test_route_new_city_los_angeles(mock_llm):
    result = await build_route("losangeles", "downtown LA", mock_llm)
    assert result.stadium == "SoFi Stadium"
    assert result.estimated_minutes > 0


async def test_route_new_city_toronto(mock_llm):
    result = await build_route("toronto", "union station", mock_llm)
    assert result.stadium == "BMO Field"
