# JDBCX MCP Server

pydbcx-mcp is a Python implementation of MCP server for enabling communication with diverse data sources via JDBCX server.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green)
[![smithery badge](https://smithery.ai/badge/@jdbcx/pydbcx-mcp)](https://smithery.ai/server/@jdbcx/pydbcx-mcp)

![image](https://github.com/user-attachments/assets/9a63dbba-64fa-424c-b399-40199dc2b820)

## Installation

### Start JDBCX server

Starts the JDBCX server container. Check out [here](https://github.com/jdbcx/jdbcx/tree/main/server) for more information.

```bash
# Start the server
docker run --rm --name bridge -d -p8080:8080 jdbcx/jdbcx server
# Test if the server if ready
curl -v 'http://localhost:8080/config'
# Check server logs
docker logs --tail=100 -f bridge
# Shutdown the server
docker stop bridge
```

### Configure MCP server

To install JDBCX MCP server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@jdbcx/pydbcx-mcp):

```bash
npx -y @smithery/cli install @jdbcx/pydbcx-mcp --client claude
```

Alternatively, add the MCP server into your JSON config file.

> Development/Unpublished Server Configuration

```json
{
  "mcpServers": {
    "jdbcx": {
      "command": "uv",
      "args": [
        "--directory",
        "</path/to/your/pydbcx-mcp/dir>",
        "run",
        "pydbcx-mcp"
      ],
      "env": {
        "JDBCX_SERVER_URL": "http://localhost:8080/",
        "JDBCX_SERVER_TOKEN": "",
        "MAX_ROWS_LIMIT": "5000"
      }
    }
  }
}
```

> Published Server Configuration

```json
{
  "mcpServers": {
    "jdbcx": {
      "command": "uvx",
      "args": ["pydbcx-mcp"],
      "env": {
        "DEFAULT_DATA_FORMAT": "md"
      }
    }
  }
}
```

> Published SSE Server Configuration

```json
{
  "mcpServers": {
    "jdbcx": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

Note: remember to start the SSE server first by `JDBCX_SERVER_URL=http://localhost:8080/ uvx pydbcx-mcp --transport sse`.

## Configuration

Configure the server using environment variables:

| Variable                        | Description                            | Default                 |
| ------------------------------- | -------------------------------------- | ----------------------- |
| `JDBCX_LOG_LEVEL`               | Log level                              | `DEBUG`                 |
| `JDBCX_SERVER_URL`              | JDBCX server URL                       | `http://localhost:8080` |
| `JDBCX_SERVER_TOKEN`            | JDBCX server access token              | None                    |
| `DEFAULT_QUERY_TIMEOUT_SECONDS` | Default query timeout (seconds)        | `10`                    |
| `DEFAULT_DATA_FORMAT`           | Default data format (md, jsonl, csv)   | `csv`                   |
| `DEFAULT_ROWS_LIMIT`            | Default number of rows can be returned | `100`                   |
| `MAX_ROWS_LIMIT`                | Maximum number of rows can be returned | `1000`                  |
| `MCP_TRANSPORT`                 | MCP server transport (stdio, see)      | `stdio`                 |
| `MCP_SERVER_HOST`               | MCP server listening address           | `0.0.0.0`               |
| `MCP_SERVER_PORT`               | MCP server listening port              | `8080`                  |
| `MCP_SERVER_NAME`               | MCP server name                        | `JDBCX MCP Server`      |

Note: It is highly recommended to enable access token in JDBCX server and configure `JDBCX_SERVER_TOKEN` accordingly for security reason.
