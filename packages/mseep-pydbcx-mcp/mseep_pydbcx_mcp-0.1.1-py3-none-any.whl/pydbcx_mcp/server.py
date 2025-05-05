import httpx
import logging
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Literal

load_dotenv()

logging.basicConfig(
    level=os.getenv("JDBCX_LOG_LEVEL", "DEBUG"),
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

JDBCX_SERVER_URL = os.getenv("JDBCX_SERVER_URL", "http://localhost:8080").rstrip("/")
JDBCX_SERVER_TOKEN = os.getenv("JDBCX_SERVER_TOKEN", "")

DEFAULT_QUERY_TIMEOUT_SECONDS = int(os.getenv("DEFAULT_QUERY_TIMEOUT_SECONDS", 10))
DEFAULT_DATA_FORMAT = os.getenv("DEFAULT_DATA_FORMAT", "csv")
DEFAULT_ROWS_LIMIT = int(os.getenv("DEFAULT_ROWS_LIMIT", 100))

MAX_ROWS_LIMIT = int(os.getenv("MAX_ROWS_LIMIT", 1000))

# instantiate an MCP server client
mcp = FastMCP(
    os.getenv("MCP_SERVER_NAME", "JDBCX MCP Server"),
    host=os.getenv("MCP_SERVER_HOST", "localhost"),
    port=os.getenv("MCP_SERVER_PORT", "8000"),
    api_key=os.getenv("MCP_API_KEY", ""),
)


def get(
    path: str, timeout_seconds: int = DEFAULT_QUERY_TIMEOUT_SECONDS, params: dict = None
) -> str:
    """Send a GET request to the JDBCX server.

    Args:
        path (str): The API endpoint path to request (without the base URL)
        timeout_seconds (int, optional): Maximum time to wait for the request in seconds.
            Defaults to DEFAULT_QUERY_TIMEOUT_SECONDS.
        params (dict, optional): Query parameters to include in the request.
            Defaults to None.

    Returns:
        str: The response text from the server
    """
    url = f"{JDBCX_SERVER_URL}/{path}"

    logging.debug(f"Getting content from [{url}] (params={params})")

    response = httpx.get(
        url,
        params=params,
        headers=(
            {"Authorization": f"Bearer {JDBCX_SERVER_TOKEN}"}
            if JDBCX_SERVER_TOKEN
            else None
        ),
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.text


def post(
    path: str,
    body: str,
    timeout_seconds: int = DEFAULT_QUERY_TIMEOUT_SECONDS,
    params: dict = None,
) -> str:
    """Send a POST request to the JDBCX server.

    Args:
        path (str): The API endpoint path to request (without the base URL)
        body (str): The content to send in the request body
        timeout_seconds (int, optional): Maximum time to wait for the request in seconds.
            Defaults to DEFAULT_QUERY_TIMEOUT_SECONDS.
        params (dict, optional): Query parameters to include in the request.
            Defaults to None.

    Returns:
        str: The response text from the server
    """
    url = f"{JDBCX_SERVER_URL}/{path}"

    logging.debug(
        f"Posting the following content to [{url}] (params={params}):\n{body}"
    )

    # use httpx to post query to the server
    response = httpx.post(
        url,
        params=params,
        headers=(
            {"Authorization": f"Bearer {JDBCX_SERVER_TOKEN}"}
            if JDBCX_SERVER_TOKEN
            else None
        ),
        content=body,
        timeout=timeout_seconds,
    )

    # logging.debug(f"Received response from the database: {response}")

    response.raise_for_status()
    return response.text


@mcp.tool()
def list_database_servers(
    query_timeout_seconds: int = DEFAULT_QUERY_TIMEOUT_SECONDS,
) -> str:
    """List all available database servers configured in the JDBCX server.

    Args:
        query_timeout_seconds (int, optional): Maximum time to wait for the request in seconds.
            Defaults to DEFAULT_QUERY_TIMEOUT_SECONDS.

    Returns:
        str: JSON string containing the list of database servers along with their corresponding descriptions
    """
    return get("config/db", timeout_seconds=query_timeout_seconds)


@mcp.tool()
def inspect_database_server(
    database_server: str,
    query_timeout_seconds: int = DEFAULT_QUERY_TIMEOUT_SECONDS,
) -> str:
    """Get detailed configuration information for a specific database server.

    Args:
        database_server (str): The name of the database server to inspect
        query_timeout_seconds (int, optional): Maximum time to wait for the request in seconds.
            Defaults to DEFAULT_QUERY_TIMEOUT_SECONDS.

    Returns:
        str: JSON string containing the detailed configuration of the specified database server
    """
    return get(f"config/db/{database_server}", timeout_seconds=query_timeout_seconds)


@mcp.tool()
def query_database(
    database_server: str,
    sql_query: str,
    query_timeout_seconds: int = DEFAULT_QUERY_TIMEOUT_SECONDS,
    data_format: Literal["md", "jsonl", "csv"] = DEFAULT_DATA_FORMAT,
    rows_limit: int = DEFAULT_ROWS_LIMIT,
) -> str:
    """Execute a SQL query against a specified database server and return formatted results.

    Args:
        database_server (str): The name of the database server to query (must be registered)
        sql_query (str): The SQL query to execute (will be wrapped in a SELECT statement)
        query_timeout_seconds (int, optional): Maximum time in seconds to wait for query execution.
            Defaults to DEFAULT_QUERY_TIMEOUT_SECONDS.
        data_format (str, optional): Output format for results. Options:
            "md" - Markdown table format
            "jsonl" - JSON Lines format (one JSON object per row)
            "csv" - Comma-separated values with header row
            Defaults to DEFAULT_DATA_FORMAT.
        rows_limit (int, optional): Maximum number of rows to return. Defaults to DEFAULT_ROWS_LIMIT.

    Returns:
        str: Query results as a string in the specified format
    """
    sql = "SELECT * FROM {{ table.db.%s: %s }} LIMIT %d" % (
        database_server,
        sql_query.replace("}}", "\\}\\}"),
        (
            DEFAULT_ROWS_LIMIT
            if rows_limit <= 0
            else (rows_limit if rows_limit <= MAX_ROWS_LIMIT else MAX_ROWS_LIMIT)
        ),
    )
    return post(
        "query", sql, timeout_seconds=query_timeout_seconds, params={"f": data_format}
    )
