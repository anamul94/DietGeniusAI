from typing import Optional
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain.chat_models import init_chat_model

from app.core.config import Settings
from psycopg import Connection
from langmem import  create_memory_store_manager, create_memory_manager


from app.agents.models.model_provider import ModelProvider
from app.constants import models, agent_const
from app.constants.prompts import qa

settings = Settings()

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}
embeddings = ModelProvider.bedrock_embeddings(
    id=models.TITAN_EMBED_TEXT
)
conn = Connection.connect(settings.DATABASE_URL, **connection_kwargs)
store = PostgresStore(conn=conn,
                      index={"embed": embeddings, "dims": 768})
store.setup()

model_id = f"""bedrock:{models.ANTHROPIC_HAIKU_3}"""
llm = init_chat_model(model_id)
store_manager = create_memory_store_manager(
    llm,
    instructions=qa.memory_extractor_sys_prompt,
    namespace=agent_const.NAMESPACE,
    store=store)
