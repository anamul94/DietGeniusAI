import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from agno.models.aws import AwsBedrock
from agno.agent import Agent
from app.constants.bedrock import NOVA_PRO, ANTHROPIC_SONNET_3_5
from typing import Optional
from model_provider import ModelProvider
model = ModelProvider(max_tokens=54, temperature=9)
bed = model.aws_model(id=ANTHROPIC_SONNET_3_5)
def get_bedrock_model(model:str,
                      max_tokens: Optional[int] = None,
                      temperature: Optional[float] = 0.0):
    return AwsBedrock(
        id=model,
        max_tokens=max_tokens,
        temperature=temperature
    )
