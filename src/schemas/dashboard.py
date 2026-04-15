from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlantCard(BaseModel):
    id: int
    name: str
    species: Optional[str]
    moisture_percent: Optional[float]
    moisture_status: str  # ok, dry, wet, no_data
    last_reading_at: Optional[datetime]
    sensor_status: str  # online, offline, no_sensor
    unread_recommendations: int


class DashboardStats(BaseModel):
    total_plants: int
    need_water: int
    sensors_online: int
    sensors_total: int
    unread_recommendations: int


class DashboardOut(BaseModel):
    stats: DashboardStats
    plants: list[PlantCard]
