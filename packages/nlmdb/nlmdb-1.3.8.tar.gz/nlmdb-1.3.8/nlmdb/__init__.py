"""
Natural Language Model Database (NLMDB) package.

This package provides a way to query databases using natural language
through the Model Context Protocol (MCP) approach.
"""

from .config import Config
from .database.handler import DatabaseHandler
from .database.tools import DatabaseTools
from .mcp.handler import MCPHandler
from .agents.agent_factory import create_database_agent

# Import the simplified API
from ._api import dbagent
from ._private_api import dbagent_private

# Import the SQL-only mode
from ._sql_agent import sql_agent, sql_agent_private

# Import the visualization agent
from ._viz_agent import viz_agent, viz_agent_private

__version__ = "1.3.1"  # Update version number
__all__ = [
    "Config",
    "DatabaseHandler",
    "DatabaseTools",
    "MCPHandler", 
    "create_database_agent",
    "dbagent",
    "dbagent_private",
    "sql_agent",
    "sql_agent_private",
    "viz_agent",
    "viz_agent_private"
]