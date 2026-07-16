from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_llm, get_workforce_cache
from ..llm.base import LLMClient
from ..schemas import BriefingResponse, WorkforceOptimizeResponse
from ..security import enforce_rate_limit, require_ops_key
from ..workforce.genetic_algorithm import WorkforceGA
from ..workforce.messaging import draft_briefing

router = APIRouter(prefix="/api/workforce", tags=["workforce"])


def _to_response(result: Any, total_shifts: int) -> WorkforceOptimizeResponse:
    filled = total_shifts - result.unfilled_shifts
    return WorkforceOptimizeResponse(
        fitness=result.fitness,
        generations_run=result.generations_run,
        unfilled_shifts=result.unfilled_shifts,
        constraint_violations=result.constraint_violations,
        total_shifts=total_shifts,
        filled_percent=round(100 * filled / total_shifts, 1) if total_shifts else 0.0,
        assignment=result.assignment,
    )


@router.post(
    "/optimize",
    response_model=WorkforceOptimizeResponse,
    dependencies=[Depends(require_ops_key), Depends(enforce_rate_limit)],
)
async def optimize(cache: dict[str, Any] = Depends(get_workforce_cache)) -> WorkforceOptimizeResponse:
    ga = WorkforceGA(cache["volunteers"], cache["shifts"], seed=None)
    result = ga.run()
    cache["result"] = result
    return _to_response(result, len(cache["shifts"]))


@router.get(
    "/briefing/{volunteer_id}",
    response_model=BriefingResponse,
    dependencies=[Depends(require_ops_key), Depends(enforce_rate_limit)],
)
async def briefing(
    volunteer_id: str,
    llm: LLMClient = Depends(get_llm),
    cache: dict[str, Any] = Depends(get_workforce_cache),
) -> BriefingResponse:
    volunteer = next((v for v in cache["volunteers"] if v.volunteer_id == volunteer_id), None)
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Unknown volunteer id")

    result = cache["result"]
    if result is None:
        raise HTTPException(status_code=503, detail="Workforce optimizer is still warming up")
    assigned_shift_ids = {sid for sid, vid in result.assignment.items() if vid == volunteer_id}
    assigned_shifts = [s for s in cache["shifts"] if s.shift_id in assigned_shift_ids]

    message = await draft_briefing(volunteer, assigned_shifts, llm)
    return BriefingResponse(volunteer_id=volunteer.volunteer_id, volunteer_name=volunteer.name, message=message)
