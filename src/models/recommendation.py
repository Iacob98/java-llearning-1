from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(
        Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message = Column(Text, nullable=False)
    rec_type = Column(String(20), nullable=False)  # water, info, warning, critical
    source = Column(String(20), nullable=False, default="auto")  # auto, user
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    is_read = Column(Boolean, nullable=False, default=False)

    plant = relationship("Plant", back_populates="recommendations")
