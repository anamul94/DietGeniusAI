from pydantic import BaseModel, Field

class AgentQA(BaseModel):
    question: str = Field(..., description="Question asked to the Patient on onboarding. For mutliple question provide in markdown format ")
    is_done: bool = Field(False, description="Wheather QA is done or not")