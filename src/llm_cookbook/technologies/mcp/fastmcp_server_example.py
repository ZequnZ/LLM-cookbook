# math_server.py
from fastmcp import FastMCP

mcp = FastMCP("Example Math Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Adds two numbers"""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers"""
    return a * b


if __name__ == "__main__":
    mcp.run()  # Uses STDIO transport by default
