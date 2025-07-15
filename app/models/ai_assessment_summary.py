from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class AIAssessmentSummary(Base):
    """
    Model for storing AI-generated daily assessment summaries
    """
    __tablename__ = "ai_assessment_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_value = Column(Date, nullable=False)
    summary = Column(Text, nullable=False)  # Markdown formatted summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_assessment_summaries")

    # Unique constraint to ensure only one summary per user per date
    __table_args__ = (
        UniqueConstraint('user_id', 'date_value', name='_user_date_summary_uc'),
    )