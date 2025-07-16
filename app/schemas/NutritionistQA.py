from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class InputType(str, Enum):
    RADIO = "radio"
    CHECKBOX = "checkbox"
    TEXTINPUT = "textinput"


class Question(BaseModel):
    question_text: str = Field(
        ...,
        description=(
            "A clear and specific question to ask the patient. "
            "Markdown formatting is allowed for readability (e.g., lists, emphasis). "
            "Questions should encourage thoughtful, detailed answers if open-ended."
        )
    )
    input_type: InputType = Field(
        ...,
        description="The type of input expected from the patient: 'radio', 'checkbox', or 'textinput'."
    )
    options: Optional[List[str]] = Field(
        None,
        description=(
            "If 'radio' or 'checkbox' is selected as input_type, provide the list of possible options here. "
            "For 'textinput', this should be None."
        )
    )
    placeholder: Optional[str] = Field(
        None,
        description=(
            "An optional placeholder text to display in the input field as an example or hint. "
            "Most relevant for 'textinput', but can be used for guidance in others if needed."
        )
    )
    additional_context: Optional[str] = Field(
        None,
        description="Optional additional context for why this question is being asked, to help the LLM generate better follow-ups."
    )


class NutritionistQA(BaseModel):
    questions: List[Question] = Field(
        ...,
        description="A list of one or more questions the LLM (Nutritionist) will ask the patient."
    )
    is_complete: bool = Field(
        False,
        description=(
            "Indicates whether the QA session is complete. "
            "If True, the frontend can redirect the user to the next page."
        )
    )
    message_on_completion: Optional[str] = Field(
        None,
        description=(
            "A final message to display to the user upon completion of the QA session. "
            "For example: 'Thank you for completing your assessment. Redirecting to dashboard...'"
        )
    )

