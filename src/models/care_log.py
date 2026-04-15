from sqlalchemy import Column, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base


class CareLog(Base):
    __tablename__ = "care_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(
        Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action = Column(String(50), nullable=False)  # watered, fertilized, repotted, pruned, misted
    notes = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())

    plant = relationship("Plant", back_populates="care_logs")
