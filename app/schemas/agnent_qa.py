from pydantic import BaseModel, Field

class AgentQA(BaseModel):
    follow_up_question: str = Field(
       "..., description="
       "Follow-up questions posed to the patient during the initial onboarding process. "
       "Provide each question in markdown format (e.g., ```markdown\nQuestion 1\nQuestion 2\n```). "
       "This allows for clear separation of multiple questions and improves readability for the LLM. "
       "Include context-specific questions relevant to the patient's situation, such as inquiries about medical history, current symptoms, or medication adherence. "
       "Consider including open-ended questions to encourage detailed patient responses."
   ),
    is_done: bool = Field(False, description="Wheather QA is done or not")