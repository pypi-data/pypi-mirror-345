from fastmcp import FastMCP, Client

mcp = FastMCP("Bus Mgmt MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

def main():
    print("bus-mgmt-mcp-server is running")
    mcp.run()
