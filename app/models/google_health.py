from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class GoogleHealthToken(Base):
    __tablename__ = "google_health_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_type = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    scope = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="google_health_tokens")

class GoogleHealthData(Base):
    __tablename__ = "google_health_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type = Column(String, nullable=False)  # e.g., "steps", "heart_rate", "sleep"
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    value = Column(JSON, nullable=False)  # Store the actual data as JSON
    source = Column(String, nullable=True)  # Source of the data (e.g., "Google Fit")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="google_health_data")

# Add a unique constraint to prevent duplicate data
# This ensures we don't save the same data point multiple times
GoogleHealthData.__table_args__ = (
    # Unique constraint on user_id, data_type, start_time, end_time
    # This prevents duplicate data for the same time period
    {'sqlite_autoincrement': True},
)