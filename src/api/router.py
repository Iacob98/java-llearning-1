from fastapi import APIRouter

from src.api.care import router as care_router
from src.api.chat import router as chat_router
from src.api.dashboard import router as dashboard_router
from src.api.plants import router as plants_router
from src.api.readings import router as readings_router
from src.api.recommendations import router as recommendations_router
from src.api.sensors import router as sensors_router

api_router = APIRouter(prefix="/api")

api_router.include_router(sensors_router, tags=["sensors"])
api_router.include_router(plants_router, tags=["plants"])
api_router.include_router(readings_router, tags=["readings"])
api_router.include_router(recommendations_router, tags=["recommendations"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(care_router, tags=["care"])
api_router.include_router(dashboard_router, tags=["dashboard"])
