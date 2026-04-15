from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RecommendationOut(BaseModel):
    id: int
    plant_id: int
    message: str
    rec_type: str
    source: str
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class AskRequest(BaseModel):
    message: str


class AskResponse(BaseModel):
    answer: str
    recommendation_id: Optional[int] = None
