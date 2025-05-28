# MCP

ref:
- [MCP](https://modelcontextprotocol.io/introduction)

[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)

Run MCP Inspector to check out MCP Server from localhost:

```bash
mcp dev PYTHON_SCRIPT.py
```

### FastMCP

[FastMCP](https://gofastmcp.com/getting-started/welcome) is a great Python implementation of MCP with enhanced features.

There are two examples in this directory:

- [fastmcp_server_example.py](fastmcp_server_example.py)
- [fastmcp_client_example.py](fastmcp_client_example.py)

To run the MCP Inspector, use the following command:

```bash
fastmcp dev fastmcp_server_example.py
```

To run the client that calls the MCP Server using STDIO as transport, use the following command:

```bash
uv run python fastmcp_client_example.py
```
