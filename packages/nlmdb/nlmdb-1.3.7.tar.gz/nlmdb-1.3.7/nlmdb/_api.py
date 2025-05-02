"""
Simplified API interface for the nlmdb package.
"""

import os
from typing import Dict, Any, Optional

from openai import OpenAI
from .config import Config
from .database.handler import DatabaseHandler
from .database.tools import DatabaseTools
from .mcp.handler import MCPHandler
from .agents.agent_factory import create_database_agent


def dbagent(api_key: str, db_path: str, query: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Main entry point for the nlmdb package.
    
    This function sets up all the necessary components and executes
    the query against the database using the MCP approach.
    
    Args:
        api_key: OpenAI API key
        db_path: Path to the SQLite database
        query: User query to execute
        verbose: Whether to enable verbose output
        
    Returns:
        The response from the agent, containing the 'output' key with
        the answer to the query.
    """
    # Initialize configuration
    config = Config(openai_api_key=api_key, db_path=db_path)
    
    # Initialize database handler
    db_handler = DatabaseHandler(config.db_path)
    
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
        verbose=verbose
    )
    
    # Execute the query
    response = agent_executor.invoke({
        "input": query,
        "chat_history": []
    })
    
    return response