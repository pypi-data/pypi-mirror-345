"""Setup script for Kaggle MCP."""

from setuptools import setup, find_packages

setup(
    name="mseep-kaggle-mcp",
    version="0.1.0",
    description="MCP server for Kaggle API integration",
    author="Kaggle MCP Contributors",
    author_email="54yyyu@example.com",
    url="https://github.com/54yyyu/kaggle-mcp",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.6.0",
        "kaggle>=1.5.0",
        "uvicorn>=0.23.2",
    ],
    entry_points={
        "console_scripts": [
            "kaggle-mcp=kaggle_mcp.server:main",
            "kaggle-mcp-setup=kaggle_mcp.setup_helper:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="kaggle, claude, ai, mcp, model-context-protocol",
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/54yyyu/kaggle-mcp/issues",
        "Source": "https://github.com/54yyyu/kaggle-mcp",
    },
)
