import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .llm import build_llm_client
from .logging_config import configure_logging
from .rag.loader import load_knowledge_base
from .routers import accessibility, dashboard, multilingual, navigation, ops, sustainability, transit, workforce
from .sensors.simulator import SensorSimulator
from .workforce.demo_data import build_demo_workforce
from .workforce.genetic_algorithm import WorkforceGA

STATIC_DIR = Path(__file__).parent.parent / "static"

logger = logging.getLogger("stadiumpulse")
configure_logging()


async def _warm_up_workforce(application: FastAPI) -> None:
    volunteers, shifts = build_demo_workforce()
    loop = asyncio.get_running_loop()
    initial_result = await loop.run_in_executor(None, lambda: WorkforceGA(volunteers, shifts, seed=42).run())
    application.state.workforce_cache = {"volunteers": volunteers, "shifts": shifts, "result": initial_result}
    logger.info("Workforce GA warm-up complete")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    application.state.llm = build_llm_client(settings)
    application.state.store = await load_knowledge_base(application.state.llm)
    application.state.sensors = SensorSimulator()

    volunteers, shifts = build_demo_workforce()
    application.state.workforce_cache = {"volunteers": volunteers, "shifts": shifts, "result": None}

    warmup_task = asyncio.create_task(_warm_up_workforce(application))

    yield

    warmup_task.cancel()
    if hasattr(application.state.llm, "aclose"):
        await application.state.llm.aclose()


app = FastAPI(title="StadiumPulse AI", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(ops.router)
app.include_router(transit.router)
app.include_router(navigation.router)
app.include_router(workforce.router)
app.include_router(accessibility.router)
app.include_router(multilingual.router)
app.include_router(sustainability.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_provider": get_settings().active_llm_provider}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
