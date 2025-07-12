import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from typing import Optional
from app.constants.bedrock import ANTHROPIC_SONNET_3
from agno.models.aws import AwsBedrock
class ModelProvider:
    def __init__(self,
                 max_tokens: Optional[int] = None,
                      temperature: Optional[float] = 0.0):
        self.max_tokens = max_tokens
        self.temperature = temperature
       
    def aws_model(
       id: str = ANTHROPIC_SONNET_3,
    ):
        return AwsBedrock(
            id=id,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )