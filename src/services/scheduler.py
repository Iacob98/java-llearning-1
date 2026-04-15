import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.plant import Plant
from src.models.sensor import Sensor
from src.services.llm_service import LLMService
from src.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def periodic_moisture_check():
    """Check all plants and generate AI recommendations if needed."""
    logger.info("Running periodic moisture check...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Plant))
        plants = result.scalars().all()

        llm = LLMService()
        for plant in plants:
            try:
                engine = RecommendationEngine(llm, session)
                rec = await engine.analyze_plant(plant.id)
                if rec:
                    logger.info(
                        "Recommendation for '%s': %s - %s",
                        plant.name, rec.rec_type, rec.message[:80],
                    )
            except Exception as e:
                logger.error("Error analyzing plant '%s': %s", plant.name, e)

    logger.info("Moisture check complete.")


async def check_sensor_health():
    """Mark sensors as offline if not seen recently."""
    threshold = datetime.now(timezone.utc) - timedelta(
        minutes=settings.SENSOR_OFFLINE_THRESHOLD_MINUTES
    )

    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Sensor)
            .where(
                Sensor.status == "active",
                Sensor.last_seen < threshold,
            )
            .values(status="offline")
        )
        await session.commit()


def setup_scheduler():
    """Configure and return the scheduler with all jobs."""
    scheduler.add_job(
        periodic_moisture_check,
        "interval",
        minutes=settings.CHECK_INTERVAL_MINUTES,
        id="moisture_check",
        replace_existing=True,
    )
    scheduler.add_job(
        check_sensor_health,
        "interval",
        minutes=5,
        id="sensor_health_check",
        replace_existing=True,
    )
    return scheduler
