from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CareLogCreate(BaseModel):
    action: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = None


class CareLogOut(BaseModel):
    id: int
    plant_id: int
    action: str
    notes: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}
