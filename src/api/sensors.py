from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_session
from src.models.sensor import Sensor
from src.models.reading import SensorReading
from src.schemas.sensor import SensorDataIn, SensorDataOut, SensorOut, SensorUpdate

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.SENSOR_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@router.post("/sensors/data", response_model=SensorDataOut)
async def receive_sensor_data(
    data: SensorDataIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Receive moisture data from ESP32 sensor. Auto-registers unknown devices."""
    result = await session.execute(
        select(Sensor).where(Sensor.esp_device_id == data.esp_device_id)
    )
    sensor = result.scalar_one_or_none()

    if sensor is None:
        sensor = Sensor(
            esp_device_id=data.esp_device_id,
            status="active",
            last_seen=datetime.now(timezone.utc),
        )
        session.add(sensor)
        await session.flush()

    sensor.last_seen = datetime.now(timezone.utc)
    sensor.status = "active"

    reading = SensorReading(
        sensor_id=sensor.id,
        moisture_percent=data.moisture_percent,
        temperature=data.temperature,
        battery_level=data.battery_level,
        raw_value=data.raw_value,
    )
    session.add(reading)
    await session.commit()

    plant_name = None
    if sensor.plant_id:
        from src.models.plant import Plant

        plant_result = await session.execute(
            select(Plant.name).where(Plant.id == sensor.plant_id)
        )
        plant_name = plant_result.scalar_one_or_none()

    return SensorDataOut(
        status="ok",
        sensor_id=sensor.id,
        plant_name=plant_name,
    )


@router.get("/sensors", response_model=list[SensorOut])
async def list_sensors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Sensor).order_by(Sensor.created_at.desc()))
    return result.scalars().all()


@router.put("/sensors/{sensor_id}", response_model=SensorOut)
async def update_sensor(
    sensor_id: int,
    data: SensorUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sensor, field, value)

    await session.commit()
    await session.refresh(sensor)
    return sensor
