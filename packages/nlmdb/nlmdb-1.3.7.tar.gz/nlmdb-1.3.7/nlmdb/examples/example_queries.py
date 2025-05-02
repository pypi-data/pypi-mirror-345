"""
Example queries for the MCP library.

This module provides example functions for querying databases using the MCP approach.
"""

from typing import Dict, Any

from ..agents.agent_factory import create_database_agent
from ..database.handler import DatabaseHandler
from ..database.tools import DatabaseTools
from ..mcp.handler import MCPHandler
from ..config import Config

from openai import OpenAI


def run_examples(api_key: str = None, db_path: str = None):
    """
    Run example queries using the MCP library.
    
    Args:
        api_key: Optional OpenAI API key. If None, will use the Config class.
        db_path: Optional path to the database. If None, will use the Config class.
    """
    # Initialize configuration
    config = Config(openai_api_key=api_key, db_path=db_path)
    
    # Initialize database handler and create sample database
    db_handler = DatabaseHandler(config.db_path)
    db_handler.create_sample_database()
    
    # Initialize database tools
    db_tools = DatabaseTools(db_handler)
    tools = db_tools.get_tools()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=config.openai_api_key)
    
    # Initialize MCP handler
    mcp_handler = MCPHandler(client, db_handler)
    
    # Create agent executor
    agent_executor = create_database_agent(
        openai_api_key=config.openai_api_key,
        tools=tools,
        mcp_handler=mcp_handler,
        verbose=True
    )
    
    print("\nExample 1: Basic Table Information")
    print("---------------------------------")
    response = example_table_info(agent_executor)
    print(response)
    
    print("\nExample 2: Simple Query")
    print("---------------------------------")
    response = example_query(agent_executor)
    print(response)
    
    print("\nExample 3: Complex Query")
    print("---------------------------------")
    response = example_complex_query(agent_executor)
    print(response)
    
    print("\nExample 4: Direct MCP Query")
    print("---------------------------------")
    response = example_direct_mcp(mcp_handler)
    print(response)


def example_table_info(agent_executor) -> str:
    """
    Example function to get basic table information.
    
    Args:
        agent_executor: An AgentExecutor instance.
        
    Returns:
        The response from the agent.
    """
    response = agent_executor.invoke({"input": "What tables are in the database and what fields do they have?"})
    return response["output"]


def example_query(agent_executor) -> str:
    """
    Example function to run a simple query.
    
    Args:
        agent_executor: An AgentExecutor instance.
        
    Returns:
        The response from the agent.
    """
    response = agent_executor.invoke({"input": "Show me all users and their ages."})
    return response["output"]


def example_complex_query(agent_executor) -> str:
    """
    Example function to run a more complex query.
    
    Args:
        agent_executor: An AgentExecutor instance.
        
    Returns:
        The response from the agent.
    """
    response = agent_executor.invoke({
        "input": "Find the total amount spent by each user and list them in descending order.",
        "chat_history": []
    })
    return response["output"]


def example_direct_mcp(mcp_handler: MCPHandler) -> str:
    """
    Example function for a direct MCP query without an agent.
    
    Args:
        mcp_handler: A MCPHandler instance.
        
    Returns:
        The response from the model.
    """
    query = "Based on the database schema, write a SQL query to find all products with inventory less than 30."
    response = mcp_handler.query_with_context(
        query,
        system_message="You are a helpful SQL assistant. Generate only SQL code without explanation."
    )
    return response


if __name__ == "__main__":
    run_examples()