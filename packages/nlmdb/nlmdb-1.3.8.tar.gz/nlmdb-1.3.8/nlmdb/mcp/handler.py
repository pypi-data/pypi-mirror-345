"""
Model Context Protocol handler module.

This module provides a handler for Model Context Protocol operations.
"""

from typing import Dict, List, Any, Optional
from openai import OpenAI

from ..database.handler import DatabaseHandler


class MCPHandler:
    """Handler for Model Context Protocol operations."""
    
    def __init__(self, client: OpenAI, db_handler: DatabaseHandler):
        """
        Initialize the MCP handler with an OpenAI client and database handler.
        
        Args:
            client: An OpenAI client instance.
            db_handler: A DatabaseHandler instance.
        """
        self.client = client
        self.db_handler = db_handler
    
    def get_database_context(self) -> str:
        """
        Generate a context message about the database structure.
        
        Returns:
            A string containing the database schema context.
        """
        tables = self.db_handler.get_tables()
        context = "Database Schema:\n"
        
        for table in tables:
            schema = self.db_handler.get_table_schema(table)
            context += f"\nTable: {table}\n"
            context += "Columns:\n"
            
            for col in schema:
                context += f"  - {col['name']} ({col['type']})"
                if col['pk'] == 1:
                    context += " PRIMARY KEY"
                if col['notnull'] == 1:
                    context += " NOT NULL"
                context += "\n"
        
        return context
    
    def query_with_context(self, query: str, model: str = "gpt-4-turbo", 
                          system_message: Optional[str] = None) -> str:
        """
        Query the model with database context and optional system message.
        
        Args:
            query: The user query to send to the model.
            model: The OpenAI model to use, defaults to "gpt-4-turbo".
            system_message: An optional system message to include.
            
        Returns:
            The model's response content.
        """
        db_context = self.get_database_context()
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add database context
        messages.append({
            "role": "system", 
            "content": f"Here is the context about the database structure:\n{db_context}"
        })
        
        # Add user query
        messages.append({"role": "user", "content": query})
        
        # Make the API call
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        
        return response.choices[0].message.content