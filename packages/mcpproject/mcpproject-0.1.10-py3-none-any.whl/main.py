from mcp.server.stdio import stdio_server


# Add an addition tool

async def addme(a: int, b: int) -> int:
    from mcp.server import Server

# Create an MCP server
    mcp = Server("geocount")
    @mcp.list_tools()
    async def list_tools() -> list:
        """List all available tools"""
        return ["add", "subtract"]

    @mcp.call_tool()
    async def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    # @mcp.call_tool()
    # async def subtract(a: int, b: int) -> int:
    #     """Subtract two numbers"""
    #     return a - b


    # Add a dynamic greeting resource
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        return f"Hello, {name}!"
    
    options = mcp.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, options)



if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
            description="give a model the ability to handle time queries and timezone conversions"
        )
    parser.add_argument("--local-timezone", type=str, help="Override local timezone")

    args = parser.parse_args()
    asyncio.run(addme(args.local_timezone))
 