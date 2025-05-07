import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo", port=8000)

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to the user."""
    return f"Hello, {name}!"


def main():
    print("Hello from mcp-test!")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')



