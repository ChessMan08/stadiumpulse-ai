from fastapi import APIRouter, Depends, HTTPException

from ..accessibility.commentary import DEMO_EVENTS, generate_commentary, get_event
from ..dependencies import get_llm
from ..llm.base import LLMClient
from ..schemas import CommentaryRequest, CommentaryResponse
from ..security import enforce_rate_limit

router = APIRouter(prefix="/api/accessibility", tags=["accessibility"])


@router.get("/events")
async def events() -> list[dict[str, object]]:
    return DEMO_EVENTS


@router.post(
    "/commentary",
    response_model=CommentaryResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def commentary(body: CommentaryRequest, llm: LLMClient = Depends(get_llm)) -> CommentaryResponse:
    try:
        event = get_event(body.event_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown event id") from None
    return await generate_commentary(event, llm, language=body.language, verbosity=body.verbosity)
