from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_session
from src.models.plant import Plant
from src.models.reading import SensorReading
from src.models.recommendation import Recommendation
from src.models.sensor import Sensor
from src.schemas.dashboard import DashboardOut, DashboardStats, PlantCard

router = APIRouter()


@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(session: AsyncSession = Depends(get_session)):
    plants_result = await session.execute(
        select(Plant).options(selectinload(Plant.sensors)).order_by(Plant.name)
    )
    plants = plants_result.scalars().all()

    now = datetime.now(timezone.utc)
    offline_threshold = now - timedelta(minutes=settings.SENSOR_OFFLINE_THRESHOLD_MINUTES)

    plant_cards = []
    need_water = 0
    sensors_online = 0
    sensors_total = 0

    for plant in plants:
        sensors_total += len(plant.sensors)

        # Get latest reading from any sensor linked to this plant
        latest_reading = None
        sensor_status = "no_sensor"

        if plant.sensors:
            sensor_ids = [s.id for s in plant.sensors]
            any_online = any(
                s.last_seen and s.last_seen >= offline_threshold for s in plant.sensors
            )
            sensor_status = "online" if any_online else "offline"
            if any_online:
                sensors_online += sum(
                    1
                    for s in plant.sensors
                    if s.last_seen and s.last_seen >= offline_threshold
                )

            reading_result = await session.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id.in_(sensor_ids))
                .order_by(SensorReading.timestamp.desc())
                .limit(1)
            )
            latest_reading = reading_result.scalar_one_or_none()

        moisture = latest_reading.moisture_percent if latest_reading else None
        if moisture is None:
            moisture_status = "no_data"
        elif moisture < plant.optimal_moisture_min:
            moisture_status = "dry"
            need_water += 1
        elif moisture > plant.optimal_moisture_max:
            moisture_status = "wet"
        else:
            moisture_status = "ok"

        # Count unread recommendations
        unread_result = await session.execute(
            select(func.count())
            .select_from(Recommendation)
            .where(
                Recommendation.plant_id == plant.id,
                Recommendation.is_read == False,  # noqa: E712
            )
        )
        unread_count = unread_result.scalar() or 0

        plant_cards.append(
            PlantCard(
                id=plant.id,
                name=plant.name,
                species=plant.species,
                moisture_percent=moisture,
                moisture_status=moisture_status,
                last_reading_at=latest_reading.timestamp if latest_reading else None,
                sensor_status=sensor_status,
                unread_recommendations=unread_count,
            )
        )

    # Total unread recommendations
    total_unread_result = await session.execute(
        select(func.count())
        .select_from(Recommendation)
        .where(Recommendation.is_read == False)  # noqa: E712
    )
    total_unread = total_unread_result.scalar() or 0

    return DashboardOut(
        stats=DashboardStats(
            total_plants=len(plants),
            need_water=need_water,
            sensors_online=sensors_online,
            sensors_total=sensors_total,
            unread_recommendations=total_unread,
        ),
        plants=plant_cards,
    )
