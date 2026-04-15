from sqlalchemy import CheckConstraint, Column, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    species = Column(String(200), nullable=True)
    optimal_moisture_min = Column(Integer, nullable=False, default=30)
    optimal_moisture_max = Column(Integer, nullable=False, default=70)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sensors = relationship("Sensor", back_populates="plant", cascade="all, delete-orphan")
    recommendations = relationship(
        "Recommendation", back_populates="plant", cascade="all, delete-orphan"
    )
    care_logs = relationship(
        "CareLog", back_populates="plant", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "optimal_moisture_min >= 0 AND optimal_moisture_min <= 100",
            name="ck_moisture_min_range",
        ),
        CheckConstraint(
            "optimal_moisture_max >= 0 AND optimal_moisture_max <= 100",
            name="ck_moisture_max_range",
        ),
        CheckConstraint(
            "optimal_moisture_min < optimal_moisture_max",
            name="ck_moisture_min_lt_max",
        ),
    )
