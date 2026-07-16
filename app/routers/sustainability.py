from fastapi import APIRouter, Depends

from ..dependencies import get_llm, get_sensors
from ..llm.base import LLMClient
from ..schemas import SustainabilityReportResponse, ZoneEstimateOut
from ..security import enforce_rate_limit
from ..sensors.simulator import SensorSimulator
from ..sustainability import build_report

router = APIRouter(prefix="/api/sustainability", tags=["sustainability"])


@router.get("/report", response_model=SustainabilityReportResponse, dependencies=[Depends(enforce_rate_limit)])
async def report(
    llm: LLMClient = Depends(get_llm),
    sim: SensorSimulator = Depends(get_sensors),
) -> SustainabilityReportResponse:
    result = await build_report(sim.snapshot(), llm)
    return SustainabilityReportResponse(
        zones=[ZoneEstimateOut.model_validate(z, from_attributes=True) for z in result.zones],
        total_estimated_kw=result.total_estimated_kw,
        total_potential_savings_kw=result.total_potential_savings_kw,
        reducible_zones=result.reducible_zones,
        tip=result.tip,
    )
