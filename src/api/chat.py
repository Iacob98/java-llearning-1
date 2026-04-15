from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.plant import Plant
from src.models.recommendation import Recommendation
from src.schemas.recommendation import AskRequest, AskResponse
from src.services.llm_service import LLMService
from src.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.post("/plants/{plant_id}/ask", response_model=AskResponse)
async def ask_about_plant(
    plant_id: int,
    request: AskRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    plant = result.scalar_one_or_none()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    llm = LLMService()
    engine = RecommendationEngine(llm, session)

    answer, recommendation = await engine.ask_about_plant(plant_id, request.message)

    return AskResponse(
        answer=answer,
        recommendation_id=recommendation.id if recommendation else None,
    )
