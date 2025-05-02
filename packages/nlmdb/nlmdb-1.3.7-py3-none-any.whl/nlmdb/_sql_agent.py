"""
SQL agent implementation for the NLMDB library.
"""

from typing import Dict, Any, Union, List, Optional, Tuple, Literal
import json
import warnings
import pandas as pd
import re

# Filter out specific warning categories
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from langchain_huggingface import HuggingFaceEndpoint
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    _has_hf_support = True
except ImportError:
    _has_hf_support = False

from .config import Config
from .database.handler import DatabaseHandler
from .database.tools import DatabaseTools


# Helper function to clean SQL queries
def clean_sql_query(sql_query: str) -> str:
    """
    Remove markdown formatting and other non-SQL content from generated SQL queries.
    
    Args:
        sql_query: The raw SQL query that might contain markdown or other formatting
        
    Returns:
        A clean SQL query string ready for execution
    """
    # Remove markdown SQL code blocks
    sql_query = re.sub(r'```sql\s*|\s*```', '', sql_query)
    
    # Remove any other code block markers
    sql_query = re.sub(r'```\w*\s*|\s*```', '', sql_query)
    
    # Remove any leading/trailing whitespace
    sql_query = sql_query.strip()
    
    return sql_query


def sql_agent(
    api_key: str,
    db_path: str,
    query: str,
    return_type: Literal["dataframe", "dict", "json"] = "dataframe",
    model_kwargs: Optional[Dict[str, Any]] = None
) -> Union[pd.DataFrame, Dict, str]:
    """
    Execute a natural language query and return only the SQL results without explanations.
    
    Args:
        api_key: OpenAI API key.
        db_path: Path to the SQLite database.
        query: User query in natural language.
        return_type: Type of return value - "dataframe", "dict", or "json".
        model_kwargs: Additional keyword arguments to pass to the model.
        
    Returns:
        The query results in the specified format.
    """
    # Set up default model_kwargs if not provided
    if model_kwargs is None:
        model_kwargs = {
            "temperature": 0.1,
            "max_tokens": 512,
        }
    
    # Initialize database handler
    db_handler = DatabaseHandler(db_path)
    
    # Get database schema for context
    def get_database_context():
        """Generate a context message about the database structure."""
        tables = db_handler.get_tables()
        context = "Database Schema:\n"
        
        for table in tables:
            schema = db_handler.get_table_schema(table)
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
    
    # Initialize OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Define the prompt template for SQL query generation
    db_query_prompt = """You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{db_schema}

The user has asked the following query:
{query}

Generate a SQL query that would answer this question.
IMPORTANT: Return ONLY the exact SQL query - no explanations, no markdown formatting (no ```sql tags), no comments, just the raw SQL.
"""
    
    # Generate the SQL query
    messages = [
        {"role": "system", "content": db_query_prompt.format(
            db_schema=get_database_context(),
            query=query
        )}
    ]
    
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        **model_kwargs
    )
    
    sql_query = completion.choices[0].message.content.strip()
    
    # Clean the SQL query
    sql_query = clean_sql_query(sql_query)
    
    # Execute the SQL query
    try:
        # Find the SQL query tool
        db_tools = DatabaseTools(db_handler)
        tools = db_tools.get_tools()
        
        sql_tool = None
        for tool in tools:
            if tool.name == "run_sql_query":
                sql_tool = tool
                break
        
        if sql_tool:
            result = sql_tool.invoke({"query": sql_query})
            
            # Get results from the returned dictionary
            if "results" in result and isinstance(result["results"], list):
                raw_results = result["results"]
                
                # Return in the requested format
                if return_type == "dataframe":
                    # Convert to DataFrame
                    if raw_results:
                        df = pd.DataFrame(raw_results)
                        return df
                    else:
                        return pd.DataFrame()
                
                elif return_type == "dict":
                    return {"sql": sql_query, "results": raw_results}
                
                elif return_type == "json":
                    return json.dumps({"sql": sql_query, "results": raw_results}, indent=2)
                
            else:
                # Handle non-standard result format
                if return_type == "dataframe":
                    return pd.DataFrame([{"error": "No results or unexpected result format", "sql": sql_query}])
                elif return_type == "dict":
                    return {"sql": sql_query, "error": "No results or unexpected result format", "raw_result": result}
                else:
                    return json.dumps({"sql": sql_query, "error": "No results or unexpected result format"})
        else:
            if return_type == "dataframe":
                return pd.DataFrame([{"error": "SQL query tool not found"}])
            elif return_type == "dict":
                return {"error": "SQL query tool not found"}
            else:
                return json.dumps({"error": "SQL query tool not found"})
                
    except Exception as e:
        error_msg = f"Error executing SQL query: {str(e)}"
        if return_type == "dataframe":
            return pd.DataFrame([{"error": error_msg, "sql": sql_query}])
        elif return_type == "dict":
            return {"sql": sql_query, "error": error_msg}
        else:
            return json.dumps({"sql": sql_query, "error": error_msg})


def sql_agent_private(
    hf_config: Union[Dict[str, str], Tuple[str, str]], 
    db_path: str, 
    query: str,
    return_type: Literal["dataframe", "dict", "json"] = "dataframe",
    model_kwargs: Optional[Dict[str, Any]] = None,
    use_local: bool = False
) -> Union[pd.DataFrame, Dict, str]:
    """
    Execute a natural language query using Hugging Face models and return only the SQL results without explanations.
    
    Args:
        hf_config: Either a dictionary with 'token' and 'model_repo' keys, or a tuple
                  with (token, model_repo) values.
        db_path: Path to the SQLite database.
        query: User query in natural language.
        return_type: Type of return value - "dataframe", "dict", or "json".
        model_kwargs: Additional keyword arguments to pass to the model.
        use_local: Whether to use a local model with HuggingFacePipeline instead of the API.
        
    Returns:
        The query results in the specified format.
    """
    if not _has_hf_support:
        raise ImportError(
            "The langchain-huggingface package is required to use sql_agent_private. "
            "Please install it with: pip install langchain-huggingface"
        )
    
    # Process the hf_config
    if isinstance(hf_config, tuple) and len(hf_config) == 2:
        hf_token, model_repo = hf_config
    elif isinstance(hf_config, dict) and 'token' in hf_config and 'model_repo' in hf_config:
        hf_token = hf_config['token']
        model_repo = hf_config['model_repo']
    else:
        raise ValueError(
            "hf_config must be either a tuple (token, model_repo) or a dictionary "
            "with 'token' and 'model_repo' keys."
        )
    
    # Set up default model_kwargs if not provided
    if model_kwargs is None:
        model_kwargs = {
            "max_new_tokens": 512,
            "do_sample": False,
            "temperature": 0.1,
            "repetition_penalty": 1.03,
        }
    
    # Make sure task is set only once
    endpoint_kwargs = model_kwargs.copy()
    if "task" in endpoint_kwargs:
        task = endpoint_kwargs.pop("task")
    else:
        task = "text-generation"  # Default task
    
    # Initialize database handler
    db_handler = DatabaseHandler(db_path)
    
    # Get database schema for context
    def get_database_context():
        """Generate a context message about the database structure."""
        tables = db_handler.get_tables()
        context = "Database Schema:\n"
        
        for table in tables:
            schema = db_handler.get_table_schema(table)
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
    
    # Initialize the LLM
    try:
        if use_local:
            # Use a local model with HuggingFacePipeline
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                
                # Load the model and tokenizer
                tokenizer = AutoTokenizer.from_pretrained(model_repo)
                model = AutoModelForCausalLM.from_pretrained(model_repo)
                
                # Create the pipeline
                pipe = pipeline(
                    task,
                    model=model,
                    tokenizer=tokenizer,
                    **endpoint_kwargs
                )
                
                # Create the LangChain wrapper
                from langchain_huggingface import HuggingFacePipeline
                llm = HuggingFacePipeline(pipeline=pipe)
            except Exception as e:
                raise RuntimeError(f"Failed to load local model: {str(e)}") from e
        else:
            # Use the Hugging Face Inference API
            llm = HuggingFaceEndpoint(
                repo_id=model_repo,
                huggingfacehub_api_token=hf_token,
                task=task,
                **endpoint_kwargs
            )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Hugging Face model: {str(e)}") from e
    
    # Define the prompt template for SQL query generation
    db_query_prompt = PromptTemplate(
        input_variables=["db_schema", "query"],
        template="""You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{db_schema}

The user has asked the following query:
{query}

Generate a SQL query that would answer this question.
IMPORTANT: Return ONLY the exact SQL query - no explanations, no markdown formatting (no ```sql tags), no comments, just the raw SQL.
"""
    )
    
    # Create the simplified pipeline for SQL generation
    sql_chain = (
        {"db_schema": lambda _: get_database_context(), "query": lambda x: x}
        | db_query_prompt
        | llm
        | StrOutputParser()
    )
    
    # Execute the SQL query and get results
    try:
        # Generate the SQL query
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sql_query = sql_chain.invoke(query)
        
        # Clean the SQL query
        sql_query = clean_sql_query(sql_query)
        
        # Execute the query
        db_tools = DatabaseTools(db_handler)
        tools = db_tools.get_tools()
        
        sql_tool = None
        for tool in tools:
            if tool.name == "run_sql_query":
                sql_tool = tool
                break
        
        if sql_tool:
            result = sql_tool.invoke({"query": sql_query})
            
            # Get results from the returned dictionary
            if "results" in result and isinstance(result["results"], list):
                raw_results = result["results"]
                
                # Return in the requested format
                if return_type == "dataframe":
                    # Convert to DataFrame
                    if raw_results:
                        df = pd.DataFrame(raw_results)
                        return df
                    else:
                        return pd.DataFrame()
                
                elif return_type == "dict":
                    return {"sql": sql_query, "results": raw_results}
                
                elif return_type == "json":
                    return json.dumps({"sql": sql_query, "results": raw_results}, indent=2)
                
            else:
                # Handle non-standard result format
                if return_type == "dataframe":
                    return pd.DataFrame([{"error": "No results or unexpected result format", "sql": sql_query}])
                elif return_type == "dict":
                    return {"sql": sql_query, "error": "No results or unexpected result format", "raw_result": result}
                else:
                    return json.dumps({"sql": sql_query, "error": "No results or unexpected result format"})
        else:
            if return_type == "dataframe":
                return pd.DataFrame([{"error": "SQL query tool not found"}])
            elif return_type == "dict":
                return {"error": "SQL query tool not found"}
            else:
                return json.dumps({"error": "SQL query tool not found"})
                
    except Exception as e:
        error_msg = f"Error executing SQL query: {str(e)}"
        if return_type == "dataframe":
            return pd.DataFrame([{"error": error_msg, "sql": sql_query}])
        elif return_type == "dict":
            return {"sql": sql_query, "error": error_msg}
        else:
            return json.dumps({"sql": sql_query, "error": error_msg})