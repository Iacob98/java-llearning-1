from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.plant import Plant
from src.schemas.plant import PlantCreate, PlantOut, PlantUpdate

router = APIRouter()


@router.get("/plants", response_model=list[PlantOut])
async def list_plants(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Plant).order_by(Plant.created_at.desc()))
    return result.scalars().all()


@router.get("/plants/{plant_id}", response_model=PlantOut)
async def get_plant(plant_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@router.post("/plants", response_model=PlantOut, status_code=201)
async def create_plant(
    data: PlantCreate, session: AsyncSession = Depends(get_session)
):
    if data.optimal_moisture_min >= data.optimal_moisture_max:
        raise HTTPException(
            status_code=422,
            detail="optimal_moisture_min must be less than optimal_moisture_max",
        )

    plant = Plant(**data.model_dump())
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    return plant


@router.put("/plants/{plant_id}", response_model=PlantOut)
async def update_plant(
    plant_id: int,
    data: PlantUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plant, field, value)

    new_min = update_data.get("optimal_moisture_min", plant.optimal_moisture_min)
    new_max = update_data.get("optimal_moisture_max", plant.optimal_moisture_max)
    if new_min >= new_max:
        raise HTTPException(
            status_code=422,
            detail="optimal_moisture_min must be less than optimal_moisture_max",
        )

    await session.commit()
    await session.refresh(plant)
    return plant


@router.delete("/plants/{plant_id}", status_code=204)
async def delete_plant(plant_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    await session.delete(plant)
    await session.commit()
