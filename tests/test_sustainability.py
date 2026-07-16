from app.sensors.simulator import GateReading, SensorSnapshot
from app.sustainability import build_report, compute_zones


def _snapshot(density: float, temp: float) -> SensorSnapshot:
    return SensorSnapshot(
        timestamp=0.0,
        readings=[
            GateReading("North", density=density, temperature_c=temp, air_quality_index=50),
            GateReading("South", density=density, temperature_c=temp, air_quality_index=50),
        ],
    )


def test_higher_density_increases_estimated_load():
    low = compute_zones(_snapshot(density=0.5, temp=22.0))
    high = compute_zones(_snapshot(density=5.0, temp=22.0))
    assert high[0].estimated_kw > low[0].estimated_kw


def test_low_density_zone_is_flagged_reducible():
    zones = compute_zones(_snapshot(density=0.5, temp=22.0))
    assert all(z.reducible for z in zones)
    assert all(z.potential_savings_kw > 0 for z in zones)


def test_comfortable_zone_is_not_reducible():
    zones = compute_zones(_snapshot(density=2.5, temp=22.0))
    assert not any(z.reducible for z in zones)


async def test_build_report_totals_match_zone_sums(mock_llm):
    report = await build_report(_snapshot(density=0.5, temp=22.0), mock_llm)
    assert report.total_estimated_kw == round(sum(z.estimated_kw for z in report.zones), 1)
    assert report.reducible_zones == [z.gate for z in report.zones if z.reducible]
    assert report.tip
