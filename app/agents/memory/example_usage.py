"""
Example usage of the generic checkpointer module.
This demonstrates how to use the checkpointer in other services.
"""

from app.agents.memory import CheckpointerManager, get_checkpointer

# Example 1: Using the default checkpointer
def example_default_checkpointer():
    """Example of using the default checkpointer."""
    checkpointer = get_checkpointer()
    return checkpointer

# Example 2: Using custom table name
def example_custom_table():
    """Example of using a custom table name."""
    checkpointer = CheckpointerManager.get_postgres_checkpointer(
        table_name="custom_checkpoints",
        schema="public"
    )
    return checkpointer

# Example 3: Using custom connection string
def example_custom_connection():
    """Example of using a custom connection string."""
    custom_db_url = "postgresql://user:pass@localhost:5432/custom_db"
    checkpointer = CheckpointerManager.get_postgres_checkpointer(
        connection_string=custom_db_url,
        table_name="service_checkpoints"
    )
    return checkpointer

# Example 4: Integration with LangGraph
def example_langgraph_integration():
    """Example of integrating with LangGraph."""
    from langgraph.graph import StateGraph, START, END
    
    # Define your state
    from typing_extensions import TypedDict
    
    class ExampleState(TypedDict):
        message: str
        count: int
    
    # Create checkpointer
    checkpointer = get_checkpointer()
    
    # Build graph
    graph_builder = StateGraph(ExampleState)
    
    # Add nodes and edges...
    # graph_builder.add_node("node_name", node_function)
    # graph_builder.add_edge(START, "node_name")
    # graph_builder.add_edge("node_name", END)
    
    # Compile with checkpointer
    # graph = graph_builder.compile(checkpointer=checkpointer)
    
    return checkpointer

if __name__ == "__main__":
    # Test the checkpointer
    cp = example_default_checkpointer()
    print("Checkpointer created successfully:", type(cp))