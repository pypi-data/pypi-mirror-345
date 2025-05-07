from mcp.server import NotificationOptions,Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from pydantic import Field
import asyncio
import click
import mcp.types as types

async def serve(auth_token: str = Field(None, description="The authentication token for the server.")
) -> Server:    
    ## auth_token 等于123456才算通过验证
    # if auth_token != "123456":
    #     raise ValueError("auth_token is invalid")
    
    server = Server("mcp-server-stdio")
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="add",
                description="""add two numbers""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "string",
                            "description": "number a",
                        },
                        "b": {
                            "type": "string",
                            "description": "number b",
                        },

                    },
                    "required": ["a", "b"]
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "add":
            if not arguments or "a" not in arguments or "b" not in arguments:
                raise ValueError("Missing a or b argument")
            return [types.TextContent(type="text", text=str(int(arguments["a"]) + int(arguments["b"])))]
    return server
   

def main():     
    print("Server started")
    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            server = await serve()
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name= server.name,
                    server_version="0.0.1",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )            
    asyncio.run(_run())
