from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.care_log import CareLog
from src.models.plant import Plant
from src.schemas.care_log import CareLogCreate, CareLogOut

router = APIRouter()


@router.post("/plants/{plant_id}/care", response_model=CareLogOut, status_code=201)
async def log_care_action(
    plant_id: int,
    data: CareLogCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plant not found")

    log = CareLog(plant_id=plant_id, **data.model_dump())
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


@router.get("/plants/{plant_id}/care", response_model=list[CareLogOut])
async def get_care_logs(
    plant_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plant not found")

    logs = await session.execute(
        select(CareLog)
        .where(CareLog.plant_id == plant_id)
        .order_by(CareLog.timestamp.desc())
        .limit(100)
    )
    return logs.scalars().all()
