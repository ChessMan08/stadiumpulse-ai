from fastapi import APIRouter, Depends

from ..dependencies import get_llm, get_sensors
from ..llm.base import LLMClient
from ..navigation.wayfinder import wayfind
from ..schemas import WayfindRequest, WayfindResponse
from ..security import enforce_rate_limit
from ..sensors.simulator import SensorSimulator

router = APIRouter(prefix="/api/navigation", tags=["navigation"])


@router.post("/wayfind", response_model=WayfindResponse, dependencies=[Depends(enforce_rate_limit)])
async def wayfind_route(
    body: WayfindRequest,
    llm: LLMClient = Depends(get_llm),
    sim: SensorSimulator = Depends(get_sensors),
) -> WayfindResponse:
    return await wayfind(body.section, body.amenity, llm, snapshot=sim.snapshot(), language=body.language)
