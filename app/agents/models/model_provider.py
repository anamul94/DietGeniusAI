import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from typing import Optional
from app.constants.bedrock import ANTHROPIC_SONNET_3
from agno.models.aws import AwsBedrock
class ModelProvider:
    def __init__(self):
        pass
        
       
    def aws_model(
       self,
       id: str = ANTHROPIC_SONNET_3,
       max_tokens: Optional[int] = None,
       temperature: Optional[float] = 0.0
    ):
        return AwsBedrock(
            id=id,
            max_tokens=max_tokens,
            temperature=temperature
        )