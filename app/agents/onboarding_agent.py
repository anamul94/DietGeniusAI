import json
from textwrap import dedent

# from app.constants import bedrock
from app.core.config import Settings

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from app.schemas.qa import QAAnsReq, QAState, QA
from app.schemas.NutritionistQA import NutritionistQA
from langchain_aws import ChatBedrock
from app.constants import models
from app.constants.prompts import qa

from psycopg import Connection


settings = Settings()
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

conn = Connection.connect(settings.DATABASE_URL, **connection_kwargs)

checkpointer = PostgresSaver(conn)
checkpointer.setup()

def qa_node(state: QAState):
    """
    This function is a node in the state graph. It takes in a state and returns a NutritionistQA object.
    """
    # Create a new instance of the ChatBedrock class
    print("Creating ChatBedrock instance")
    chat_bedrock = ChatBedrock(
        model=models.NOVA_PRO,
        temperature=0.1,
        beta_use_converse_api=True,
    )
    llm_with_structured_output = chat_bedrock.with_structured_output(NutritionistQA)
    system_message = qa.qa_prompt
    
    # user_message = {
    #     "user_response": state["qa"],
    #     "medical_report": state["medical_report"],
    #     "qa round numer": state["count"],
    # }
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": state["message"]},
    ]
    
    response = llm_with_structured_output.invoke(messages)
    # print(response)
    # print("Parsing Response")
    # qa_data = NutritionistQA(response)
    # print(qa_data)
    return {"questions": response}

graph_builder = StateGraph(QAState)

graph_builder.add_node("qa_node", qa_node)
graph_builder.add_edge(START, "qa_node")
graph_builder.add_edge("qa_node", END)
graph = graph_builder.compile(checkpointer=checkpointer)

def generate_summary(config):
    checkpointer(graph)
        
        
    