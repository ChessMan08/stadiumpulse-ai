import pytest
from fastapi.testclient import TestClient

from app.llm.mock_client import MockLLMClient
from app.main import app
from app.sensors.simulator import GateReading, SensorSnapshot


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_llm() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture
def calm_snapshot() -> SensorSnapshot:
    return SensorSnapshot(
        timestamp=0.0,
        readings=[
            GateReading("North", density=1.0, temperature_c=22.0, air_quality_index=50),
            GateReading("South", density=1.0, temperature_c=22.0, air_quality_index=50),
        ],
    )


@pytest.fixture
def congested_snapshot() -> SensorSnapshot:
    return SensorSnapshot(
        timestamp=0.0,
        readings=[
            GateReading("North", density=4.5, temperature_c=22.0, air_quality_index=50),
            GateReading("South", density=1.0, temperature_c=22.0, air_quality_index=50),
        ],
    )
