"""
Private API implementation using Hugging Face models with clean output.
"""

from typing import Dict, Any, Union, List, Optional, Tuple
import re
import json
import warnings
import logging

# Filter out specific warning categories
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set up a logger to capture and redirect warnings
logger = logging.getLogger("huggingface_hub")
logger.setLevel(logging.ERROR)  # Only log errors, not warnings

try:
    from langchain_huggingface import HuggingFaceEndpoint, HuggingFacePipeline
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    _has_hf_support = True
except ImportError:
    _has_hf_support = False

from .config import Config
from .database.handler import DatabaseHandler
from .database.tools import DatabaseTools


def dbagent_private(hf_config: Union[Dict[str, str], Tuple[str, str]], 
                  db_path: str, 
                  query: str, 
                  verbose: bool = False,
                  model_kwargs: Optional[Dict[str, Any]] = None,
                  use_local: bool = False) -> Dict[str, Any]:
    """
    An alternative to dbagent that uses Hugging Face models instead of OpenAI.
    
    Args:
        hf_config: Either a dictionary with 'token' and 'model_repo' keys, or a tuple
                  with (token, model_repo) values.
        db_path: Path to the SQLite database.
        query: User query to execute.
        verbose: Whether to enable verbose output.
        model_kwargs: Additional keyword arguments to pass to the model.
        use_local: Whether to use a local model with HuggingFacePipeline instead of the API.
        
    Returns:
        The response from the agent, containing the 'output' key with
        the answer to the query.
    
    Raises:
        ImportError: If the langchain-huggingface package is not installed.
    """
    if not _has_hf_support:
        raise ImportError(
            "The langchain-huggingface package is required to use dbagent_private. "
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
    
    # Initialize database tools
    db_tools = DatabaseTools(db_handler)
    tools = db_tools.get_tools()
    
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
    
    # Format the tools for the prompt
    tools_string = ""
    for tool in tools:
        tools_string += f"Tool: {tool.name}\n"
        tools_string += f"Description: {tool.description}\n"
        tools_string += "\n"
    
    # Define the prompt template for a simple database query
    db_query_prompt = PromptTemplate(
        input_variables=["db_schema", "query"],
        template="""You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{db_schema}

The user has asked the following query:
{query}

Please generate a SQL query that would answer this question. Only provide the SQL query, nothing else.
"""
    )
    
    # Define a chain to execute the SQL query
    def run_sql_query(sql_query):
        # Find the SQL query tool
        sql_tool = None
        for tool in tools:
            if tool.name == "run_sql_query":
                sql_tool = tool
                break
        
        if sql_tool:
            try:
                result = sql_tool.invoke({"query": sql_query})
                # Clean the result for better presentation
                clean_result = result
                if "results" in result and isinstance(result["results"], list):
                    # Limit to a reasonable number of rows for readability
                    if len(result["results"]) > 10:
                        clean_result = {"results": result["results"][:10], "note": f"Showing 10 of {len(result['results'])} results"}
                return clean_result
            except Exception as e:
                return f"Error executing SQL query: {str(e)}"
        else:
            return "SQL query tool not found."
    
    # Define the prompt for generating the final answer
    final_answer_prompt = PromptTemplate(
        input_variables=["db_schema", "query", "sql_query", "sql_result"],
        template="""You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{db_schema}

The user asked: {query}

To answer this question, the following SQL query was executed:
```sql
{sql_query}
```

The result of this query was:
{sql_result}

Based on this information, please provide a comprehensive answer to the user's query.
Your answer should be clear, concise, and user-friendly. Don't mention the SQL query unless it's relevant to explaining the answer.
Format your response cleanly and professionally.
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
        if verbose:
            print("Generating SQL query...")
        
        # Capture original stdout to suppress unwanted output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sql_query = sql_chain.invoke(query)
        
        if verbose:
            print(f"Generated SQL query: {sql_query}")
        
        # Execute the query
        sql_result = run_sql_query(sql_query)
        
        if verbose:
            print(f"Query execution complete.")
        
        # Generate the final answer
        final_answer_chain = (
            {
                "db_schema": lambda _: get_database_context(),
                "query": lambda _: query,
                "sql_query": lambda _: sql_query,
                "sql_result": lambda _: sql_result
            }
            | final_answer_prompt
            | llm
            | StrOutputParser()
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            final_answer = final_answer_chain.invoke({})
        
        # Clean up the final answer
        final_answer = final_answer.strip()
        # Remove any extraneous "Answer:" prefix if present
        if final_answer.lower().startswith("answer:"):
            final_answer = final_answer[7:].strip()
            
        return {"output": final_answer}
    
    except Exception as e:
        # Fallback to a simpler approach if the chain fails
        if verbose:
            print(f"Error in main chain: {str(e)}")
            print("Falling back to simpler approach...")
        
        # Simple fallback prompt
        fallback_prompt = PromptTemplate(
            input_variables=["db_schema", "query"],
            template="""You are a database expert assistant that helps users interact with databases.
You have access to the following database structure:
{db_schema}

The user has asked the following query:
{query}

Please provide a helpful response. If you need database information to answer this query,
explain what SQL query would need to be run and what information you would need to extract.
"""
        )
        
        # Create a simple fallback chain
        fallback_chain = (
            {"db_schema": lambda _: get_database_context(), "query": lambda _: query}
            | fallback_prompt
            | llm
            | StrOutputParser()
        )
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fallback_answer = fallback_chain.invoke({})
            return {"output": fallback_answer}
        except Exception as fallback_error:
            # If even the fallback fails, return a generic response
            error_message = f"Failed to generate a response: {str(fallback_error)}"
            if verbose:
                print(error_message)
            
            return {
                "output": "I'm sorry, I wasn't able to process your query due to technical difficulties. "
                         "Please try again with a different model or approach."
            }