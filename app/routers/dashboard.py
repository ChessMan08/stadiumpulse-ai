from typing import Any

from fastapi import APIRouter, Depends

from ..dependencies import get_llm, get_sensors, get_workforce_cache
from ..llm.base import LLMClient
from ..schemas import DashboardResponse, GateReadingOut, SensorSnapshotOut
from ..security import enforce_rate_limit
from ..sensors.simulator import SensorSimulator
from ..sustainability import build_report

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardResponse, dependencies=[Depends(enforce_rate_limit)])
async def summary(
    llm: LLMClient = Depends(get_llm),
    sim: SensorSimulator = Depends(get_sensors),
    cache: dict[str, Any] = Depends(get_workforce_cache),
) -> DashboardResponse:
    snapshot = sim.snapshot()
    result = cache.get("result")
    total_shifts = len(cache["shifts"])
    filled_percent = 0.0
    if result is not None and total_shifts:
        filled_percent = round(100 * (total_shifts - result.unfilled_shifts) / total_shifts, 1)

    energy = await build_report(snapshot, llm)

    return DashboardResponse(
        sensors=SensorSnapshotOut(
            timestamp=snapshot.timestamp,
            readings=[GateReadingOut.model_validate(r, from_attributes=True) for r in snapshot.readings],
        ),
        peak_gate=snapshot.peak_gate.gate,
        active_alert_count=len(snapshot.alerts),
        workforce_filled_percent=filled_percent,
        sustainability_tip=energy.tip,
        total_estimated_kw=energy.total_estimated_kw,
    )
