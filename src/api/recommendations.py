from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.plant import Plant
from src.models.recommendation import Recommendation
from src.schemas.recommendation import RecommendationOut

router = APIRouter()


@router.get("/plants/{plant_id}/recommendations", response_model=list[RecommendationOut])
async def get_recommendations(
    plant_id: int,
    unread_only: bool = False,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plant not found")

    query = (
        select(Recommendation)
        .where(Recommendation.plant_id == plant_id)
        .order_by(Recommendation.created_at.desc())
        .limit(50)
    )
    if unread_only:
        query = query.where(Recommendation.is_read == False)  # noqa: E712

    result = await session.execute(query)
    return result.scalars().all()


@router.post("/plants/{plant_id}/recommendations/{rec_id}/read")
async def mark_as_read(
    plant_id: int,
    rec_id: int,
    session: AsyncSession = Depends(get_session),
):
    await session.execute(
        update(Recommendation)
        .where(Recommendation.id == rec_id, Recommendation.plant_id == plant_id)
        .values(is_read=True)
    )
    await session.commit()
    return {"status": "ok"}
