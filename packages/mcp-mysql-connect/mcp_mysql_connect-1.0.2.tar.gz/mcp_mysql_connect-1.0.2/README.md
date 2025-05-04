# MySQL MCP Server

A Model Context Protocol (MCP) server that provides an interface for AI models to interact with MySQL databases through natural language queries.

## Overview

This package creates an MCP server that connects to a MySQL database and exposes a tool to execute SQL queries. It allows AI models like Claude to interact with your MySQL database without direct database access.

## Prerequisites

- Python 3.11 or above
- MySQL database

## Installation

You can install the MCP MySQL server using pip:

```bash
pip install mcp_mysql_connect
```

Or using UV:

```bash
uv pip install mcp_mysql_connect
```

## Configuration

The server requires the following environment variables:

- `DB_HOST` - MySQL server host
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - MySQL database name

You can set these using a `.env` file or directly in your environment.

## Usage Options

### 1. Using with Cursor

Add the following to your `~/.cursor/mcp.json` configuration:

```json
"mysql-mcp-server": {
  "command": "uvx",
  "args": [
    "--from",
    "mcp_mysql_connect",
    "mcp_mysql_connect"
  ],
  "env": {
    "DB_HOST": "your-mysql-host",
    "DB_USER": "your-username",
    "DB_PASSWORD": "your-password",
    "DB_NAME": "your-database"
  }
}
```

Alternative configuration:

```json
"mysql-mcp-server": {
  "command": "uv",
  "args": [
    "run",
    "--with",
    "mcp_mysql_connect",
    "-m",
    "mcp_mysql_connect"
  ],
  "env": {
    "DB_HOST": "your-mysql-host",
    "DB_USER": "your-username",
    "DB_PASSWORD": "your-password",
    "DB_NAME": "your-database"
  }
}
```

### 2. Using with Python Code

```python
from mcp.client import Client
from mcp.tools import Tools

# Connect to the MySQL MCP server
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

### 3. Running Manually

Start the server manually:

```bash
# Set environment variables first
export DB_HOST=your-mysql-host
export DB_USER=your-username
export DB_PASSWORD=your-password
export DB_NAME=your-database

# Then run the server
python -m mcp_mysql_connect
```

## Available Tools

The server provides a SQL execution tool that can be used to query your MySQL database:

- `read_query(query: str, params: List[str] = None)` - Execute a SQL SELECT query against the database

## Example Queries

When using with Claude or other AI models, you can ask natural language questions like:

- "Show me all users who registered in the last week"
- "What are the top 5 selling products?"
- "Count how many orders each customer has placed"

The AI model will translate these into SQL queries and use the MCP server to execute them.

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
