import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.services import router as services_router
from app.monitoring.scheduler import run_monitoring_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    monitoring_task = asyncio.create_task(run_monitoring_loop())

    try:
        yield
    finally:
        monitoring_task.cancel()
        with suppress(asyncio.CancelledError):
            await monitoring_task


app = FastAPI(
    title="StatusRadar",
    lifespan=lifespan,
)
app.include_router(services_router)


@app.get("/health")
def health():
    return {"status": "ok"}
