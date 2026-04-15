from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensorDataIn(BaseModel):
    esp_device_id: str = Field(..., min_length=1, max_length=50)
    moisture_percent: float = Field(..., ge=0, le=100)
    temperature: Optional[float] = None
    battery_level: Optional[float] = Field(None, ge=0, le=100)
    raw_value: Optional[int] = None


class SensorDataOut(BaseModel):
    status: str
    sensor_id: int
    plant_name: Optional[str] = None


class SensorOut(BaseModel):
    id: int
    plant_id: Optional[int]
    esp_device_id: str
    label: Optional[str]
    location: Optional[str]
    status: str
    last_seen: Optional[datetime]

    model_config = {"from_attributes": True}


class SensorUpdate(BaseModel):
    plant_id: Optional[int] = None
    label: Optional[str] = None
    location: Optional[str] = None
