"""
Agent factory module for the MCP library.

This module provides factory functions for creating LangChain agents.
"""

from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.chat_models import ChatOpenAI  # Updated import

from ..mcp.handler import MCPHandler
from ..database.tools import DatabaseTools


def create_database_agent(
    openai_api_key: str,
    tools: List,
    mcp_handler: MCPHandler,
    model_name: str = "gpt-4-turbo",
    temperature: float = 0,
    verbose: bool = True,
    handle_parsing_errors: bool = True
) -> AgentExecutor:
    """
    Create an agent for interacting with a database using the MCP approach.
    
    Args:
        openai_api_key: OpenAI API key.
        tools: List of LangChain tools to use.
        mcp_handler: A MCPHandler instance.
        model_name: The name of the LLM model to use.
        temperature: Temperature parameter for the LLM.
        verbose: Whether to enable verbose output.
        handle_parsing_errors: Whether to handle parsing errors.
        
    Returns:
        An AgentExecutor instance.
    """
    # System message with MCP context
    system_message = f"""You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{mcp_handler.get_database_context()}
Use the tools available to you to help the user interact with the database effectively.
Always explain your reasoning before using a tool.
Do not make up information about the database - use the tools to verify.
"""
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the LLM
    llm = ChatOpenAI(temperature=temperature, model_name=model_name, openai_api_key=openai_api_key)
    
    # Create the agent
    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=handle_parsing_errors,
    )
    
    return agent_executor