from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_llm
from ..llm.base import LLMClient
from ..multilingual.faq import FAQS, answer, list_topics
from ..schemas import FaqRequest, FaqResponse
from ..security import enforce_rate_limit

router = APIRouter(prefix="/api/multilingual", tags=["multilingual"])


@router.get("/topics")
async def topics() -> list[dict[str, str]]:
    return list_topics()


@router.post("/faq", response_model=FaqResponse, dependencies=[Depends(enforce_rate_limit)])
async def faq(body: FaqRequest, llm: LLMClient = Depends(get_llm)) -> FaqResponse:
    if body.topic_id not in FAQS:
        raise HTTPException(status_code=404, detail="Unknown topic id")
    return await answer(body.topic_id, llm, language=body.language)
