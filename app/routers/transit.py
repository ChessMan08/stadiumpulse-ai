from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_llm, get_sensors
from ..llm.base import LLMClient
from ..schemas import TransitRouteRequest, TransitRouteResponse
from ..security import enforce_rate_limit
from ..sensors.simulator import SensorSimulator
from ..transit.data import CITIES
from ..transit.router import build_route, list_cities

router = APIRouter(prefix="/api/transit", tags=["transit"])


@router.get("/cities")
async def cities() -> list[dict[str, str]]:
    return list_cities()


@router.post(
    "/route",
    response_model=TransitRouteResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def route(
    body: TransitRouteRequest,
    llm: LLMClient = Depends(get_llm),
    sim: SensorSimulator = Depends(get_sensors),
) -> TransitRouteResponse:
    if body.city not in CITIES:
        raise HTTPException(status_code=404, detail="Unknown city id")
    return await build_route(body.city, body.origin, llm, snapshot=sim.snapshot(), language=body.language)
