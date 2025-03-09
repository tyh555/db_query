# Simple MCP MySQL Server

A lightweight Model Context Protocol (MCP) server that enables secure interaction with MySQL databases. This server allows AI assistants like Claude to list tables, read data, and execute SQL queries through a controlled interface.

## Features

* List all MySQL tables in the database
* Retrieve detailed schema information for all tables
* Execute read-only SQL queries with proper error handling
* Secure database access through environment variables
* Simple configuration and deployment

## Installation

```bash
# Clone the repository
git clone git@github.com:alexcc4/mcp-mysql-server.git
cd mysql-mcp-server

# Install dependencies using uv (recommended)
uv sync

```

## Configuration

Set the following environment variables:
- export DB_HOST=localhost # Database host
- export DB_PORT=3306 # Database port (defaults to 3306 if not specified)
- export DB_USER=your_username # Database username
- export DB_PASSWORD=your_password # Database password
- export DB_NAME=your_database # Database name


## Usage

### Manual Start

```bash
uv run main.py
```

### With Claude Desktop

Add this to your Claude Desktop configuration file:

> Mac Claude Desktop config: ~/Library/Application Support/Claude/claude_desktop_config.json (create it if it doesn't exist)

```json
{
    "mcpServers": {
        "sql": {
            "command": "/path/uv",
            "args": [
                "--directory",
                "code_path",
                "run",
                "main.py"
            ],
            "env": {
                "DB_HOST": "127.0.0.1",
                "DB_PORT": "3306",
                "DB_USER": "your_user",
                "DB_PASSWORD": "your_password",
                "DB_NAME": "your_database"
           }
        }
    }
}
```

### Example Queries

Once configured, you can ask Claude questions like:
```
"Show me all tables in the database"
"Top 10 rows from users table"
"Find all orders placed in the last 30 days"
"Count of users by country"
"Show me the schema of the products table"
```

## Available Resources

The server provides the following resources:

* `mysql://schema` - Complete database structure information including all tables and columns
* `mysql://tables` - List of all tables in the database

## Available Tools

The server provides the following tools:

* `query_data` - Execute read-only SQL queries and return results

## Requirements

- uv (recommended)
- Python 3.12.2+
- MySQL server

## Security Considerations

* Use a database user with minimal required permissions (read-only)
* Never use root credentials for production environments
* Consider implementing query whitelisting for sensitive databases
* Monitor and log all database operations

## License

MIT

## Reference

- [Official Document](https://modelcontextprotocol.io/introduction)
- [PostgresSQL Demo](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)
