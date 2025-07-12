from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class QaAns(BaseModel):
    answer: str = Field(description="QA Answer Value")
    count: int = Field(description="QA Count Value", default_factory=0)
    chat_history: List[Dict[str, str]] = Field(description="QA and answer history as {question: answer}", default_factory=list)
    
class QA(BaseModel):
    question: str = Field(description="Question")
    count: int = Field(description="QA Count Value", default_factory=0)
    chat_history: List[Dict[str, str]] = Field(description="QA and answer history as {question: answer}", default_factory=list)