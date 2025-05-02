"""
Visualization agent implementation for the NLMDB library.
"""

from typing import Dict, Any, Union, List, Optional, Tuple, Literal
import json
import warnings
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
from ._sql_agent import clean_sql_query, sql_agent, sql_agent_private


def viz_agent(
    api_key: str,
    db_path: str,
    query: str,
    return_fig: bool = True,
    fig_format: Literal["plotly", "json", "html"] = "plotly",
    model_kwargs: Optional[Dict[str, Any]] = None
) -> Union[go.Figure, Dict, str]:
    """
    Generate a visualization based on a natural language query about your database.
    
    Args:
        api_key: OpenAI API key.
        db_path: Path to the SQLite database.
        query: User query in natural language (e.g., "Show me a bar chart of sales by category")
        return_fig: Whether to return the Plotly figure object (True) or the visualization spec (False)
        fig_format: If return_fig is False, the format to return the visualization in
                   ("plotly" for figure, "json" for JSON spec, "html" for HTML)
        model_kwargs: Additional keyword arguments to pass to the model.
        
    Returns:
        Either a Plotly figure object, JSON visualization spec, or HTML representation.
    """
    # Set up default model_kwargs if not provided
    if model_kwargs is None:
        model_kwargs = {
            "temperature": 0.2,  # Slightly higher temperature for more creative visualizations
            "max_tokens": 1024,
        }
    
    # First, get the data using sql_agent
    df = sql_agent(
        api_key=api_key,
        db_path=db_path,
        query=f"Generate the data needed to {query}",
        return_type="dataframe",
        model_kwargs=model_kwargs
    )
    
    # Check if we got an error
    if 'error' in df.columns and len(df) == 1:
        error_msg = df['error'].iloc[0]
        if return_fig:
            # Create an error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {error_msg}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red")
            )
            return fig
        else:
            if fig_format == "json":
                return {"error": error_msg}
            elif fig_format == "html":
                return f"<div style='color: red;'>Error: {error_msg}</div>"
            else:
                # Default to plotly figure
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Error: {error_msg}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="red")
                )
                return fig
    
    # Initialize OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Get column information for context
    column_info = "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])
    
    # Define the prompt template for visualization generation
    viz_prompt = """You are a data visualization expert that helps users create plotly visualizations.

You have access to a DataFrame with the following columns:
{column_info}

The user has asked to: {query}

Based on the data and the user's request, generate Python code to create an appropriate plotly visualization.
The code should use plotly.express or plotly.graph_objects and create a variable named 'fig'.
Include all necessary styling, titles, labels, and formatting.
Only return the Python code, nothing else.
"""
    
    # Generate the visualization code
    messages = [
        {"role": "system", "content": viz_prompt.format(
            column_info=column_info,
            query=query
        )}
    ]
    
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        **model_kwargs
    )
    
    viz_code = completion.choices[0].message.content.strip()
    
    # Extract just the code (remove any markdown formatting)
    viz_code = re.sub(r'```python\s*|\s*```', '', viz_code)
    viz_code = re.sub(r'```\w*\s*|\s*```', '', viz_code)
    
    # Execute the visualization code
    try:
        # Create a local scope
        local_vars = {"df": df, "px": px, "go": go, "make_subplots": make_subplots}
        
        # Execute the code
        exec(viz_code, globals(), local_vars)
        
        # Get the figure
        if 'fig' in local_vars:
            fig = local_vars['fig']
            
            # Return in the requested format
            if return_fig:
                return fig
            else:
                if fig_format == "json":
                    return json.loads(fig.to_json())
                elif fig_format == "html":
                    return fig.to_html()
                else:
                    return fig
        else:
            raise ValueError("Visualization code did not create a 'fig' variable")
            
    except Exception as e:
        error_msg = f"Error generating visualization: {str(e)}"
        if return_fig:
            # Create an error figure
            fig = go.Figure()
            fig.add_annotation(
                text=error_msg,
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red")
            )
            return fig
        else:
            if fig_format == "json":
                return {"error": error_msg, "code": viz_code}
            elif fig_format == "html":
                return f"<div style='color: red;'>{error_msg}</div>"
            else:
                # Default to plotly figure
                fig = go.Figure()
                fig.add_annotation(
                    text=error_msg,
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="red")
                )
                return fig


def viz_agent_private(
    hf_config: Union[Dict[str, str], Tuple[str, str]], 
    db_path: str, 
    query: str,
    return_fig: bool = True,
    fig_format: Literal["plotly", "json", "html"] = "plotly",
    model_kwargs: Optional[Dict[str, Any]] = None,
    use_local: bool = False
) -> Union[go.Figure, Dict, str]:
    """
    Generate a visualization based on a natural language query about your database using Hugging Face models.
    
    Args:
        hf_config: Either a dictionary with 'token' and 'model_repo' keys, or a tuple
                  with (token, model_repo) values.
        db_path: Path to the SQLite database.
        query: User query in natural language (e.g., "Show me a bar chart of sales by category")
        return_fig: Whether to return the Plotly figure object (True) or the visualization spec (False)
        fig_format: If return_fig is False, the format to return the visualization in
                   ("plotly" for figure, "json" for JSON spec, "html" for HTML)
        model_kwargs: Additional keyword arguments to pass to the model.
        use_local: Whether to use a local model with HuggingFacePipeline instead of the API.
        
    Returns:
        Either a Plotly figure object, JSON visualization spec, or HTML representation.
    """
    if not _has_hf_support:
        raise ImportError(
            "The langchain-huggingface package is required to use viz_agent_private. "
            "Please install it with: pip install langchain-huggingface"
        )
    
    # First, get the data using sql_agent_private
    df = sql_agent_private(
        hf_config=hf_config,
        db_path=db_path,
        query=f"Generate the data needed to {query}",
        return_type="dataframe",
        model_kwargs=model_kwargs,
        use_local=use_local
    )
    
    # Check if we got an error
    if 'error' in df.columns and len(df) == 1:
        error_msg = df['error'].iloc[0]
        if return_fig:
            # Create an error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {error_msg}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red")
            )
            return fig
        else:
            if fig_format == "json":
                return {"error": error_msg}
            elif fig_format == "html":
                return f"<div style='color: red;'>Error: {error_msg}</div>"
            else:
                # Default to plotly figure
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Error: {error_msg}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="red")
                )
                return fig
    
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
            "max_new_tokens": 1024,
            "do_sample": True,  # More creative for visualization
            "temperature": 0.4,
            "repetition_penalty": 1.03,
        }
    
    # Make sure task is set only once
    endpoint_kwargs = model_kwargs.copy()
    if "task" in endpoint_kwargs:
        task = endpoint_kwargs.pop("task")
    else:
        task = "text-generation"  # Default task
    
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
    
    # Get column information for context
    column_info = "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])
    
    # Define the prompt template for visualization generation
    viz_prompt = PromptTemplate(
        input_variables=["column_info", "query"],
        template="""You are a data visualization expert that helps users create plotly visualizations.

You have access to a DataFrame with the following columns:
{column_info}

The user has asked to: {query}

Based on the data and the user's request, generate Python code to create an appropriate plotly visualization.
The code should use plotly.express or plotly.graph_objects and create a variable named 'fig'.
Include all necessary styling, titles, labels, and formatting.
Only return the Python code, nothing else.
"""
    )
    
    # Create the pipeline for visualization code generation
    viz_chain = (
        {"column_info": lambda _: column_info, "query": lambda _: query}
        | viz_prompt
        | llm
        | StrOutputParser()
    )
    
    # Generate and execute visualization code
    try:
        # Generate the visualization code
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            viz_code = viz_chain.invoke({})
        
        # Extract just the code (remove any markdown formatting)
        viz_code = re.sub(r'```python\s*|\s*```', '', viz_code)
        viz_code = re.sub(r'```\w*\s*|\s*```', '', viz_code)
        
        # Create a local scope
        local_vars = {"df": df, "px": px, "go": go, "make_subplots": make_subplots}
        
        # Execute the code
        exec(viz_code, globals(), local_vars)
        
        # Get the figure
        if 'fig' in local_vars:
            fig = local_vars['fig']
            
            # Return in the requested format
            if return_fig:
                return fig
            else:
                if fig_format == "json":
                    return json.loads(fig.to_json())
                elif fig_format == "html":
                    return fig.to_html()
                else:
                    return fig
        else:
            raise ValueError("Visualization code did not create a 'fig' variable")
            
    except Exception as e:
        error_msg = f"Error generating visualization: {str(e)}"
        if return_fig:
            # Create an error figure
            fig = go.Figure()
            fig.add_annotation(
                text=error_msg,
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red")
            )
            return fig
        else:
            if fig_format == "json":
                return {"error": error_msg, "code": viz_code}
            elif fig_format == "html":
                return f"<div style='color: red;'>{error_msg}</div>"
            else:
                # Default to plotly figure
                fig = go.Figure()
                fig.add_annotation(
                    text=error_msg,
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="red")
                )
                return fig