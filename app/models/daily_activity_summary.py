from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Date, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class DailyActivitySummary(Base):
    __tablename__ = "daily_activity_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_value = Column(Date, nullable=False)
    datatype = Column(String, nullable=False)  # e.g., "steps", "heart_rate", "sleep", "nutrition"
    source = Column(String, nullable=False)  # e.g., "Google Fit"
    total_value = Column(JSON, nullable=False)  # Dynamic string keys with float values
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="daily_activity_summaries")

    # Unique constraint to ensure only one record per user, date, and datatype
    __table_args__ = (
        UniqueConstraint('user_id', 'date_value', 'datatype', name='_user_date_datatype_uc'),
    )