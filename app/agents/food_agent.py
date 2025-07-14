from textwrap import dedent

from agno.agent import Agent
from app.constants import bedrock, prompts
from app.agents.memory.storage import GENERAL_SESSION_STORAGE, USER_DAILY_LOG_SESSION_STORAGE
from app.agents.memory.memory import get_memory_with_manager