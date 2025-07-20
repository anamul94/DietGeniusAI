from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.schemas.NutritionistQA import NutritionistQA
import json
from typing_extensions import TypedDict

class QaAns(BaseModel):
    question: Optional[str] = Field(description="QA Question")
    answer: Optional[str] = Field(description="QA Answer Value")
    
    def __str__(self):
        return json.dumps(self.dict(), indent=2)
    
class QAAnsReq(BaseModel):
    qa: Optional[List[QaAns]] = Field(..., description="List of QA questions and answers")
    count: int = Field(default=0, description="Total count of QA items")
    medical_report: str = Field(description="QA Message", default="")

    def to_dict(self) -> dict:
        return {
            "qa": [qa.model_dump() for qa in self.qa],
            "count": self.count
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        return self.to_json()
    
    def get_combined_answers(self) -> str:
        """Get all answers combined as a single string"""
        return '\n\n'.join([f"{qa.question}: {qa.answer}" for qa in self.qa])
    
    def has_unanswered_questions(self) -> bool:
        """Check if any questions are unanswered"""
        return any(not qa.answer.strip() for qa in self.qa)

class QA(BaseModel):
    data: NutritionistQA = Field(description="Question")
    count: int = Field(description="QA Count Value", default_factory=0)
    summary: str = Field(description="QA Summary", default="")
    
    
# class QAState(TypedDict):
#     qa: List[QaAns] = Field(default_factory=list)
#     count: int = 0
#     medical_report: Optional[str] = ""
#     questions: Optional[NutritionistQA] = None   # node output
#     summary: str = ""

class QAState(TypedDict):
    message: str
    questions: Optional[NutritionistQA]