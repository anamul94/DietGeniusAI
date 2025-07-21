import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from typing import Optional
from app.constants.models import ANTHROPIC_SONNET_3
from agno.models.aws import AwsBedrock
from agno.models.ollama import Ollama
from agno.models.openrouter import OpenRouter
from agno.models.groq import Groq
from langchain_aws import ChatBedrock
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_ollama import ChatOllama


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
     
    @staticmethod   
    def ollama_model(
        self,
        id: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 0.1
    ):
        return ChatOllama(
            model=id
        )
        
    def openrouter_model(
        self,
        id: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 0.1
    ):
        return OpenRouter(
            id=id,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
    def groq_model(
        self,
        id: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 0.1
    ):
        return Groq(
            id=id,
            temperature=temperature
        )
        
    @staticmethod
    def chat_bedrock(
        id: str = ANTHROPIC_SONNET_3,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        return ChatBedrock(
            model=id,
            max_tokens=max_tokens,
            temperature=temperature,
            beta_use_converse_api=True,
        )
        
    @staticmethod
    def bedrock_embeddings(
        id: str = ANTHROPIC_SONNET_3,
        
    ):
        return BedrockEmbeddings(
            model_id=id,
           
        )