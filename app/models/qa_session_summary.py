from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class QASessionSummary(Base):
    __tablename__ = "qa_session_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # e.g., 'base_condition', 'onboarding', etc.
    summary = Column(Text, nullable=False)  # The generated summary text
    conversation_data = Column(JSON, nullable=True)  # Store the full conversation if needed
    session_metadata = Column(JSON, nullable=True)  # Additional metadata like questions count, duration, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="qa_session_summaries")