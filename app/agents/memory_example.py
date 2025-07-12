from agno.agent.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory, MemoryManager, SessionSummarizer
from rich.pretty import pprint
from agno.models.aws import AwsBedrock
from agno.memory.v2.schema import SessionSummary, UserMemory
# from app.constants.bedrock import NOVA_PRO
NOVA_PRO = "apac.amazon.nova-pro-v1:0"

memory_db = PostgresMemoryDb(table_name="memory",
                             schema="public",
                             db_url="postgresql://postgres:1234@localhost:5433/deitgeniusdb")

# You can also override the entire `system_message` for the memory manager
memory_manager = MemoryManager(
    model=AwsBedrock(id=NOVA_PRO),
    additional_instructions="""
    IMPORTANT: Don't store any memories about the user's name. Just say "The User" instead of referencing the user's name.
    """,
)

# You can also override the entire `system_message` for the session summarizer
session_summarizer = SessionSummarizer(
    model=AwsBedrock(id=NOVA_PRO),
    additional_instructions="""
    Make the summary very informal and conversational.
    """,
)

memory = Memory(
    model=AwsBedrock(id=NOVA_PRO),
    db=memory_db,
    memory_manager=memory_manager,
    summarizer=session_summarizer,
)

# Reset the memory for this example
# memory.clear()

john_doe_id = "anamul"

agent = Agent(
    model=AwsBedrock(id=NOVA_PRO),
    memory=memory,
    enable_user_memories=True,
    enable_session_summaries=True,
    user_id=john_doe_id,
)

# agent.print_response(
#     "seeking job for ai", stream=True
# )

# agent.print_response("do i suffreing any desease", stream=True)

# memory.add_user_memory(user_id=john_doe_id, memory=UserMemory(memory="how are you buddy"))
memories = memory.get_user_memories(user_id=john_doe_id)

print("John Doe's memories:")
pprint(memories)

# summary = agent.get_session_summary()
# print("Session summary:")
# pprint(summary)