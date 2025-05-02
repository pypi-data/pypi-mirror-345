# NLMDB: Natural Language & MCP-powered Database

<div align="center">

![NLMDB Logo](https://img.shields.io/badge/NLMDB-Natural%20Language%20Database-blue?style=for-the-badge&logo=database)

[![PyPI version](https://img.shields.io/pypi/v/nlmdb.svg)](https://pypi.org/project/nlmdb/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nlmdb.svg)](https://pypi.org/project/nlmdb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/nlmdb.svg)](https://pypi.org/project/nlmdb/) -->


</div>

Query your databases using natural language through the Model Context Protocol (MCP) approach. NLMDB provides a simple API for interacting with databases using either OpenAI or Hugging Face models.

## ✨ Features

- 💬 Query databases using natural language
- 🔄 Support for both OpenAI and Hugging Face models
- 🔒 Enhanced privacy options with local Hugging Face models
- 📊 Automatic schema extraction
- 📝 Multiple output formats: explanatory text or direct data
- 🧩 Simple, intuitive API

## 🚀 Installation

```bash
pip install nlmdb
```

## 🏁 Quick Start

### Natural Language Explanations Mode

```python
from nlmdb import dbagent

# Initialize the agent with your API key and database path
response = dbagent(
    api_key="your-openai-api-key",
    db_path="path/to/your/database.db",
    query="What tables are in the database and what columns do they have?"
)

print(response["output"])
```

### SQL Agent Mode (New!)

Get direct results without explanations - perfect for data analysis workflows:

```python
from nlmdb import sql_agent
import pandas as pd

# Get results as a pandas DataFrame
df = sql_agent(
    api_key="your-openai-api-key",
    db_path="path/to/your/database.db",
    query="List all customers who made purchases over $1000",
    return_type="dataframe"  # Options: "dataframe", "dict", or "json"
)

# Now you can directly work with the data
print(df.head())
```

### Using Hugging Face Models

```python
from nlmdb import dbagent_private

# Initialize the agent with your Hugging Face token and model name
response = dbagent_private(
    hf_config=("your-huggingface-token", "model-repo-name"),
    db_path="path/to/your/database.db",
    query="What tables are in the database and what columns do they have?"
)

print(response["output"])
```

## 🔒 Privacy and Data Security

NLMDB offers enhanced privacy options through its support for Hugging Face models:

### Enhanced Privacy with Hugging Face Models

When using `dbagent_private` or `sql_agent_private` with `use_local=True`, all processing happens locally on your machine, ensuring your database schema and query data never leave your environment:

```python
response = dbagent_private(
    hf_config=("your-huggingface-token", "model-repo-name"),
    db_path="path/to/your/database.db",
    query="What tables are in the database?",
    use_local=True  # Ensures all processing happens locally
)
```

### Data Security Considerations

- **OpenAI Integration**: When using `dbagent` with OpenAI models, database schema and queries are sent to OpenAI's API. While only schema information and not actual data is shared, consider privacy implications.

- **Hugging Face Cloud API**: Using `dbagent_private` without `use_local=True` sends queries to Hugging Face's Inference API.

- **Local Processing**: For maximum privacy, use `dbagent_private` with `use_local=True` to keep all processing on your machine.

- **No Data Storage**: NLMDB does not store or log your database contents, queries, or responses.

## 🔄 Model Comparison

| Feature | OpenAI Models (`dbagent`/`sql_agent`) | Hugging Face Models (`dbagent_private`/`sql_agent_private`) |
|---------|---------------------------|----------------------------------------|
| **SQL Generation Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Privacy** | ⭐⭐ | ⭐⭐⭐⭐⭐ (with `use_local=True`) |
| **Cost** | 💰💰💰 | 💰 (self-hosted) / 💰💰 (HF API) |
| **Offline Usage** | ❌ | ✅ (with `use_local=True`) |
| **Setup Complexity** | Simple | Moderate |
| **Resource Requirements** | Minimal (Cloud-based) | High (for local models) |
| **Speed** | Fast | Varies (depends on hardware) |
| **Customizability** | Limited | Extensive |

## 🧩 Advanced Usage

### SQL Agent with Different Return Types

```python
# Get results as a dictionary
result_dict = sql_agent(
    api_key="your-openai-api-key",
    db_path="path/to/your/database.db",
    query="Find the total sales by product category",
    return_type="dict"
)

# Get results as JSON
json_result = sql_agent(
    api_key="your-openai-api-key",
    db_path="path/to/your/database.db",
    query="Show me monthly sales trends",
    return_type="json"
)

# SQL Agent with Hugging Face for privacy
df = sql_agent_private(
    hf_config=("your-huggingface-token", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
    db_path="path/to/your/database.db",
    query="List customers in California",
    return_type="dataframe",
    use_local=True  # For local processing
)
```

### Customizing Model Parameters

```python
model_kwargs = {
    "temperature": 0.2,
    "max_new_tokens": 1024,
    "repetition_penalty": 1.1
}

response = dbagent_private(
    hf_config=("your-huggingface-token", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
    db_path="path/to/your/database.db",
    query="Summarize the sales data for the last quarter",
    model_kwargs=model_kwargs
)
```

## 🔍 Choosing the Right Mode & Model

### Modes

| Mode | Functions | Best For | Output |
|------|-----------|----------|--------|
| **Explanatory** | `dbagent`, `dbagent_private` | Understanding data context | Natural language explanations with insights |
| **SQL Agent** | `sql_agent`, `sql_agent_private` | Data analysis, integration | Raw data as DataFrame, dict, or JSON |

### Recommended Hugging Face Models

| Model | Performance | Resource Usage | Best For |
|-------|-------------|----------------|----------|
| **mistralai/Mixtral-8x7B-Instruct-v0.1** | ⭐⭐⭐⭐⭐ | 🖥️🖥️🖥️🖥️ | Best overall SQL generation |
| **meta-llama/Llama-2-7b-chat-hf** | ⭐⭐⭐⭐ | 🖥️🖥️🖥️ | Balance of performance and resources |
| **Qwen/Qwen2-7B-Instruct** | ⭐⭐⭐ | 🖥️🖥️ | Efficient for simpler queries |

## 📊 Supported Databases

Currently, NLMDB supports:

- SQLite ✅

Future releases will add support for:

- PostgreSQL 🔜
- MySQL 🔜
- Microsoft SQL Server 🔜

## ⚙️ Requirements

- Python 3.8+
- openai>=1.0.0
- langchain>=0.1.0
- langchain-core>=0.1.0
- langchain-community>=0.0.0
- langchain-huggingface>=0.0.1 (for Hugging Face integration)
- pandas>=1.0.0 (for DataFrame return type in SQL agent mode)

## 📜 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

<div align="center">
  
[![LangChain](https://img.shields.io/badge/Powered%20by-LangChain-blue)](https://github.com/langchain-ai/langchain)
[![OpenAI](https://img.shields.io/badge/Supports-OpenAI-lightgrey)](https://openai.com/)
[![Hugging Face](https://img.shields.io/badge/Supports-Hugging%20Face-yellow)](https://huggingface.co/)
[![SQLite](https://img.shields.io/badge/Works%20with-SQLite-blue)](https://www.sqlite.org/)
[![pandas](https://img.shields.io/badge/Integrates-pandas-150458)](https://pandas.pydata.org/)

</div>

This library is built on top of:

- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI API](https://openai.com/)
- [Hugging Face Inference API](https://huggingface.co/)
- [SQLite](https://www.sqlite.org/)
- [pandas](https://pandas.pydata.org/)