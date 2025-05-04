# MySQL MCP Server Documentation

## Overview
This repository contains the MySQL database configuration for the MCP (Model Context Protocol) server. This MCP server handles data fetching from the connected database.

## Prerequisites
- Python 3.10 or above
- pip or uv package installer
- mysql-connector-python

## Installation
```bash
# Install from PyPI
pip install mcp_mysql_connect

# Or using uv
uv pip install mcp_mysql_connect
```

## Configuration
1. Create a `.env` file in your project directory with the following environment variables:
```
DB_HOST=your_mysql_host
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
```

2. Make sure these environment variables are accessible to your application.

## Usage
```python
# Example usage with Claude
from mcp.client import Client
from mcp.tools import Tools

# Connect to your MySQL MCP server
tools = Tools()
tools.add_server("mysql", "mcp_mysql_connect")

# Create a client with the tools
client = Client(tools=tools)

# Example query
response = client.complete(
    messages=[
        {"role": "user", "content": "Query all users from the database"}
    ]
)
print(response.content)
```

## Environment Variables
Required environment variables for database connection:
- `DB_HOST` - Database host address
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Target database name

## Development
To contribute or modify this package, clone the repository and install in development mode:
```bash
git clone <repository_url>
cd MySQL-MCP-Server
python -m pip install -e .
```
