from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Scheduler will be started here after Phase 6
    yield
    await close_db()


app = FastAPI(
    title="PlantMon API",
    description="Локальная ИИ-система мониторинга влажности растений",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "plantmon"}
