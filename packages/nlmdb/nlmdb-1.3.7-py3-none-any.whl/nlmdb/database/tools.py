"""
LangChain tool implementations for database interactions.

This module provides LangChain tools for database operations.
"""

from langchain.tools import StructuredTool
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ..database.handler import DatabaseHandler


class TableNameSchema(BaseModel):
    """Schema for table name input."""
    table_name: str = Field(..., description="The name of the table to get the structure for")


class QuerySchema(BaseModel):
    """Schema for SQL query input."""
    query: str = Field(..., description="The SQL query to execute")


class DatabaseTools:
    """A class providing LangChain tools for database operations."""
    
    def __init__(self, db_handler: DatabaseHandler):
        """
        Initialize the database tools with a database handler.
        
        Args:
            db_handler: A DatabaseHandler instance for database operations.
        """
        self.db_handler = db_handler
    
    def list_database_tables(self) -> Dict[str, List[str]]:
        """
        List all tables in the connected database.
            
        Returns:
            A dictionary containing a list of table names.
        """
        tables = self.db_handler.get_tables()
        return {"tables": tables}
    
    def get_table_structure(self, table_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the structure (schema) of a specific table.
        
        Args:
            table_name: The name of the table to get the structure for.
            
        Returns:
            A dictionary containing the table schema information.
        """
        schema = self.db_handler.get_table_schema(table_name)
        return {"schema": schema}
    
    def run_sql_query(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute a SQL query against the database and return the results.
        
        Args:
            query: A SQL query string to execute.
            
        Returns:
            A dictionary containing the query results or error message.
        """
        results = self.db_handler.execute_query(query)
        return {"results": results}
    
    def get_tools(self) -> List:
        """
        Get a list of all database tools as LangChain tools.
        
        Returns:
            A list of LangChain StructuredTool objects.
        """
        return [
            StructuredTool.from_function(
                func=self.list_database_tables,
                name="list_database_tables",
                description="List all tables in the connected database."
            ),
            StructuredTool.from_function(
                func=self.get_table_structure,
                name="get_table_structure",
                description="Get the structure (schema) of a specific table.",
                args_schema=TableNameSchema
            ),
            StructuredTool.from_function(
                func=self.run_sql_query,
                name="run_sql_query",
                description="Execute a SQL query against the database and return the results.",
                args_schema=QuerySchema
            )
        ]