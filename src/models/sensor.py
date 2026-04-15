from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.dialects.sqlite import TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(
        Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    esp_device_id = Column(String(50), nullable=False, unique=True)
    label = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    last_seen = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    plant = relationship("Plant", back_populates="sensors")
    readings = relationship(
        "SensorReading", back_populates="sensor", cascade="all, delete-orphan"
    )
