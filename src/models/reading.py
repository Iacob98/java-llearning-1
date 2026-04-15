from sqlalchemy import Column, Float, ForeignKey, Index, Integer, func
from sqlalchemy.dialects.sqlite import TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base


class SensorReading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(
        Integer, ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    moisture_percent = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    battery_level = Column(Float, nullable=True)
    raw_value = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)

    sensor = relationship("Sensor", back_populates="readings")

    __table_args__ = (
        Index("ix_readings_sensor_timestamp", "sensor_id", "timestamp"),
    )
