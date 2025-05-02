"""
Setup script for the NLMDB library.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md file for the long description
try:
    this_directory = Path(__file__).parent
    long_description = (this_directory / "README.md").read_text()
except:
    long_description = "Query databases using natural language through the Model Context Protocol (MCP) approach"

setup(
    name="nlmdb",  # Using your package name
    version="1.3.7",  # Increment version for new release
    description="Natural Language Model Database - Query databases using natural language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rakshith Dharmappa",
    author_email="rakshith.officialmail@gmail.com",
    url="https://github.com/rakshithdharmap/nlmdb",  # Update with your actual GitHub URL
    project_urls={
        "Bug Tracker": "https://github.com/rakshithdharmap/nlmdb/issues",
        "Documentation": "https://github.com/rakshithdharmap/nlmdb#readme",
        "Source Code": "https://github.com/rakshithdharmap/nlmdb",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.0",
        "langchain-experimental>=0.0.0",
        "langchain-huggingface>=0.0.1",
        "timm",
        "pandas>=1.0.0",
        "plotly>=5.0.0",  # Added plotly dependency for visualization
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",  # Added visualization classifier
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="database, natural language, openai, huggingface, sql, privacy, ai, llm, mcp, visualization, plotly",
)