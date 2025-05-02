"""
Database handler module for the MCP library.

This module provides classes for interacting with SQLite databases.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Union


class DatabaseHandler:
    """A class to handle database operations."""
    
    def __init__(self, db_path: str):
        """
        Initialize the database handler with a path to the SQLite database.
        
        Args:
            db_path: Path to the SQLite database.
        """
        self.db_path = db_path
    
    def connect(self) -> sqlite3.Connection:
        """
        Create and return a database connection.
        
        Returns:
            A SQLite connection object.
        """
        return sqlite3.connect(self.db_path)
    
    def get_tables(self) -> List[str]:
        """
        Get a list of all tables in the database.
        
        Returns:
            A list of table names.
        """
        conn = self.connect()
        cursor = conn.cursor()
        # Query to get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema for a specific table.
        
        Args:
            table_name: The name of the table to get the schema for.
            
        Returns:
            A list of dictionaries containing column information.
        """
        conn = self.connect()
        cursor = conn.cursor()
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        schema = []
        for col in columns:
            schema.append({
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": col[3],
                "default_value": col[4],
                "pk": col[5]
            })
        conn.close()
        return schema
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return the results as a list of dictionaries.
        
        Args:
            query: The SQL query to execute.
            
        Returns:
            A list of dictionaries containing the query results or error message.
        """
        if "DROP" in query.upper() or "DELETE" in query.upper():
            return [{"error": "Data deletion operations are not allowed for safety reasons."}]
        
        try:
            conn = self.connect()
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            cursor.execute(query)
            
            # If SELECT query, return results
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            else:
                # For other queries (INSERT, UPDATE), commit and return affected rows
                conn.commit()
                result = [{"message": "Query executed successfully", "rows_affected": cursor.rowcount}]
            
            conn.close()
            return result
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_sample_database(self):
        """
        Create a sample SQLite database with a few tables.
        
        This method is mainly for demonstration and testing purposes.
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            inventory INTEGER DEFAULT 0
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Insert sample data
        # Users
        users_data = [
            (1, "John Doe", "john@example.com", 32),
            (2, "Jane Smith", "jane@example.com", 28),
            (3, "Bob Johnson", "bob@example.com", 45)
        ]
        
        for user in users_data:
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
                user
            )
        
        # Products
        products_data = [
            (1, "Laptop", 999.99, "Electronics", 50),
            (2, "Phone", 699.99, "Electronics", 100),
            (3, "Headphones", 199.99, "Accessories", 75)
        ]
        
        for product in products_data:
            cursor.execute(
                "INSERT OR IGNORE INTO products (id, name, price, category, inventory) VALUES (?, ?, ?, ?, ?)",
                product
            )
        
        # Orders
        orders_data = [
            (1, 1, 999.99),
            (2, 1, 199.98),
            (3, 2, 699.98)
        ]
        
        for order in orders_data:
            cursor.execute(
                "INSERT OR IGNORE INTO orders (id, user_id, total_amount) VALUES (?, ?, ?)",
                order
            )
        
        conn.commit()
        conn.close()