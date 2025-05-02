"""
Configuration module for the MCP library.

This module handles configuration settings such as API keys and database paths.
"""

import os
from typing import Optional


class Config:
    """Configuration handler for the MCP library."""
    
    def __init__(self, openai_api_key: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize the configuration with optional API key and database path.
        
        Args:
            openai_api_key: OpenAI API key. If None, will look for OPENAI_API_KEY environment variable.
            db_path: Path to the SQLite database. If None, will use a default path.
        """
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set.")
        
        self.db_path = db_path or "example.db"
        
    @classmethod
    def from_env(cls):
        """
        Create a Config instance from environment variables.
        
        Returns:
            Config: A new Config instance.
        """
        return cls(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            db_path=os.environ.get("MCP_DB_PATH", "example.db")
        )