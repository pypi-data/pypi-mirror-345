from mcp.server import Server

# Create an MCP server
mcp = Server("geocount")


# Add an addition tool
@mcp.list_tools()
async def list_tools() -> list:
    """List all available tools"""
    return ["add", "subtract"]

@mcp.call_tool()
async def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.call_tool()
async def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
 