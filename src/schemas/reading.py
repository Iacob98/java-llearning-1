from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingOut(BaseModel):
    id: int
    sensor_id: int
    moisture_percent: float
    temperature: Optional[float]
    battery_level: Optional[float]
    raw_value: Optional[int]
    timestamp: datetime

    model_config = {"from_attributes": True}


class ReadingsSummary(BaseModel):
    readings: list[ReadingOut]
    count: int
    avg_moisture: Optional[float]
    min_moisture: Optional[float]
    max_moisture: Optional[float]
