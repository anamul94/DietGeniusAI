from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.schemas.NutritionistQA import NutritionistQA

class QaAns(BaseModel):
    question: str = Field(description="QA Question")
    answer: str = Field(description="QA Answer Value")
    count: int = Field(description="QA Count Value", default_factory=0)
    
class QA(BaseModel):
    data: NutritionistQA = Field(description="Question")
    count: int = Field(description="QA Count Value", default_factory=0)
