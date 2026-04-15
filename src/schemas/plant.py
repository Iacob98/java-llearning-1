from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    species: Optional[str] = Field(None, max_length=200)
    optimal_moisture_min: int = Field(30, ge=0, le=100)
    optimal_moisture_max: int = Field(70, ge=0, le=100)
    notes: Optional[str] = None


class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, max_length=200)
    optimal_moisture_min: Optional[int] = Field(None, ge=0, le=100)
    optimal_moisture_max: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class PlantOut(BaseModel):
    id: int
    name: str
    species: Optional[str]
    optimal_moisture_min: int
    optimal_moisture_max: int
    notes: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
