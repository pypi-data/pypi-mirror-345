from mcp.server import Server

# Create an MCP server
mcp = Server("geocount")


# Add an addition tool
@mcp.list_tools()
def list_tools() -> list:
    """List all available tools"""
    return ["add", "subtract"]

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

options = mcp.create_initialization_options()

if __name__ == "__main__":
    mcp.run(read_stream=True, write_stream=True, options=options)
 