from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.plant import Plant
from src.models.reading import SensorReading
from src.models.sensor import Sensor
from src.schemas.reading import ReadingOut, ReadingsSummary

router = APIRouter()


@router.get("/plants/{plant_id}/readings", response_model=ReadingsSummary)
async def get_readings(
    plant_id: int,
    hours: int = Query(default=24, ge=1, le=720),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plant not found")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    sensor_ids_result = await session.execute(
        select(Sensor.id).where(Sensor.plant_id == plant_id)
    )
    sensor_ids = [row[0] for row in sensor_ids_result.all()]

    if not sensor_ids:
        return ReadingsSummary(
            readings=[], count=0, avg_moisture=None, min_moisture=None, max_moisture=None
        )

    query = (
        select(SensorReading)
        .where(
            SensorReading.sensor_id.in_(sensor_ids),
            SensorReading.timestamp >= since,
        )
        .order_by(SensorReading.timestamp.asc())
    )

    # Limit to 500 points; downsample if too many
    readings_result = await session.execute(query)
    all_readings = readings_result.scalars().all()

    if len(all_readings) > 500:
        step = len(all_readings) // 500
        all_readings = all_readings[::step]

    stats_query = select(
        func.avg(SensorReading.moisture_percent),
        func.min(SensorReading.moisture_percent),
        func.max(SensorReading.moisture_percent),
    ).where(
        SensorReading.sensor_id.in_(sensor_ids),
        SensorReading.timestamp >= since,
    )
    stats = await session.execute(stats_query)
    avg_m, min_m, max_m = stats.one()

    return ReadingsSummary(
        readings=[ReadingOut.model_validate(r) for r in all_readings],
        count=len(all_readings),
        avg_moisture=round(avg_m, 1) if avg_m else None,
        min_moisture=round(min_m, 1) if min_m else None,
        max_moisture=round(max_m, 1) if max_m else None,
    )
