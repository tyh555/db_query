from typing import Any, Dict
import os
import logging

import MySQLdb
from mcp.server.fastmcp import FastMCP

import dotenv

dotenv.load_dotenv()

# Create MCP server instance
mcp = FastMCP("mysql-server")

# Database connection configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "passwd": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mysql-mcp-server")


# Connect to MySQL database
def get_connection():
    try:
        return MySQLdb.connect(**DB_CONFIG)
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        raise


@mcp.resource("mysql://schema")
def get_schema() -> Dict[str, Any]:
    """Provide database table structure information"""
    conn = get_connection()
    cursor = None
    try:
        # Create dictionary cursor
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]

        # Get structure for each table
        schema = {}
        for table_name in table_names:
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            table_schema = []

            for column in columns:
                table_schema.append({
                    "name": column["Field"],
                    "type": column["Type"],
                    "null": column["Null"],
                    "key": column["Key"],
                    "default": column["Default"],
                    "extra": column["Extra"]
                })

            schema[table_name] = table_schema

        return {
            "database": DB_CONFIG["db"],
            "tables": schema
        }
    finally:
        if cursor:
            cursor.close()
        conn.close()


def is_safe_query(sql: str) -> bool:
    """Basic check for potentially unsafe queries"""
    sql_lower = sql.lower()
    unsafe_keywords = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]
    return not any(keyword in sql_lower for keyword in unsafe_keywords)


@mcp.tool()
def query_data(sql: str) -> Dict[str, Any]:
    """Execute read-only SQL queries"""
    if not is_safe_query(sql):
        return {
            "success": False,
            "error": "Potentially unsafe query detected. Only SELECT queries are allowed."
        }
    logger.info(f"Executing query: {sql}")
    conn = get_connection()
    cursor = None
    try:
        # Create dictionary cursor
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Start read-only transaction
        cursor.execute("SET TRANSACTION READ ONLY")
        cursor.execute("START TRANSACTION")

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.commit()

            # Convert results to serializable format
            return {
                "success": True,
                "results": results,
                "rowCount": len(results)
            }
        except Exception as e:
            conn.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    finally:
        if cursor:
            cursor.close()
        conn.close()


@mcp.resource("mysql://tables")
def get_tables() -> Dict[str, Any]:
    """Provide database table list"""
    conn = get_connection()
    cursor = None
    try:
        # Create dictionary cursor
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]

        return {
            "database": DB_CONFIG["db"],
            "tables": table_names
        }
    finally:
        if cursor:
            cursor.close()
        conn.close()


def validate_config():
    """Validate database configuration"""
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
        logger.warning("Using default values, which may not work in production.")


'''def main():
    validate_config()
    print(f"MySQL MCP server started, connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}")
'''
def main():
    validate_config()
    print(f"MySQL MCP server started, connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}")
    print("MCP server is running...")
    mcp.run()
    print("MCP server exited")  # mcp.run() 提前退出


if __name__ == "__main__":
    main()
    mcp.run()
