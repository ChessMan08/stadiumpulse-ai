from fastapi import APIRouter, Depends

from ..dependencies import get_llm, get_sensors, get_store
from ..llm.base import LLMClient
from ..ops.copilot import diagnose
from ..rag.store import VectorStore
from ..schemas import GateReadingOut, OpsQueryRequest, OpsQueryResponse, SensorSnapshotOut
from ..security import enforce_rate_limit, require_ops_key
from ..sensors.simulator import SensorSimulator

router = APIRouter(prefix="/api/ops", tags=["ops"])


@router.get("/sensors", response_model=SensorSnapshotOut, dependencies=[Depends(enforce_rate_limit)])
async def sensors(sim: SensorSimulator = Depends(get_sensors)) -> SensorSnapshotOut:
    snapshot = sim.snapshot()
    return SensorSnapshotOut(
        timestamp=snapshot.timestamp,
        readings=[GateReadingOut.model_validate(r, from_attributes=True) for r in snapshot.readings],
    )


@router.post(
    "/query",
    response_model=OpsQueryResponse,
    dependencies=[Depends(require_ops_key), Depends(enforce_rate_limit)],
)
async def query(
    body: OpsQueryRequest,
    llm: LLMClient = Depends(get_llm),
    store: VectorStore = Depends(get_store),
    sim: SensorSimulator = Depends(get_sensors),
) -> OpsQueryResponse:
    return await diagnose(body.question, llm, store, sim.snapshot(), language=body.language)
