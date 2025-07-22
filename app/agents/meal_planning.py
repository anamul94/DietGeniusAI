from langgraph.prebuilt import create_react_agent
from langmem import create_manage_memory_tool, create_search_memory_tool


from app.constants.prompts import meal_plan, memory_instruction
from app.constants import models
from app.constants.agent_const import NAMESPACE
from app.agents.models.model_provider import ModelProvider
from app.agents.memory.pg_store import pg_store
from app.agents.config import langfuse


def generate_meal_plan(message: str, config):
    """
    Generates a meal plan based on the provided message.
    """
    sys_prompt = meal_plan.meal_plan_gen_prompt
    agent = create_react_agent(
        model=ModelProvider.chat_bedrock(
            id=models.ANTHROPIC_SONNET_3_5, temperature=0.1
        ),
        prompt=sys_prompt,
        tools=[
            create_manage_memory_tool(
                namespace=NAMESPACE,
                instructions=memory_instruction.memory_extractor_sys_prompt,
            ),
            # create_search_memory_tool(
            #     namespace=NAMESPACE,
            # ),
        ],
        store=pg_store,
    )

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            # We will continue the conversation (thread-a) by using the config with
            # the same thread_id
        )

        print(response)
        return response["messages"][-1].content
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        return None


generate_meal_plan("dark. Remember that.", config="jlsdjk")
