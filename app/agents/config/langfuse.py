from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from langchain_core.prompts import ChatPromptTemplate
 
from app.core.config import settings
# Initialize Langfuse client with constructor arguments
Langfuse(
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    secret_key=settings.LANGFUSE_SECRET_KEY,
    host=settings.LANGFUSE_HOST  # Optional: defaults to https://cloud.langfuse.com
)
 
# Get the configured client instance
langfuse = get_client()
 
# Initialize the Langfuse handler
langfuse_handler = CallbackHandler()