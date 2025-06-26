import anyio
import json
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from .config import settings

'''
Helper function to call the chakoshi API.
'''
async def call_chakoshi(text: str) -> dict:
    """
    Calls the chakoshi moderation API with the provided text.

    Args:
        text: The text to be moderated.

    Returns:
        A dictionary containing the moderation results from the API.

    Raises:
        httpx.HTTPStatusError: If the API call returns an error status code.
    """
    payload = {
        "input": text,
        "model": settings.model_id,
        "category_set_id": settings.category_set_id,
    }
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.timeout_sec) as client:
        resp = await client.post(settings.api_url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

'''
Definition of the MCP server.
'''
def build_server() -> Server:
    """
    Builds and configures the MCP server instance.

    Returns:
        The configured MCP Server instance.
    """
    app = Server("chakoshi-moderation-server")

    # Endpoint called first by the MCP client to discover available tools.
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """
        Lists the tools available on this server.

        Returns:
            A list containing the 'moderate_text' tool definition.
        """
        return [
            types.Tool(
                name="moderate_text",
                description="Check if a text is safe using chakoshi moderation API",
                inputSchema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "Text to check"}
                    },
                },
            )
        ]

    # Endpoint called by the MCP client to execute a specific tool.
    @app.call_tool()
    async def call_tool(name: str, args: dict):
        """
        Executes the specified tool with the given arguments.

        Currently supports only the 'moderate_text' tool.

        Args:
            name: The name of the tool to call (should be 'moderate_text').
            args: A dictionary containing the arguments for the tool (expects 'text').

        Returns:
            A list containing a TextContent object with the moderation results
            (formatted as pretty JSON) or an error message.

        Raises:
            ValueError: If the tool name is unsupported or required arguments are missing.
        """
        if name != "moderate_text":
            raise ValueError(f"Unsupported tool: {name}")
        if "text" not in args:
            raise ValueError("Missing required arg 'text'")

        try:
            # Call the chakoshi API
            result = await call_chakoshi(args["text"])
            # Format the results into a user-readable format (pretty JSON)
            pretty = json.dumps(result["results"], ensure_ascii=False, indent=2)
            return [types.TextContent(type="text", text=pretty)]

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 401 Unauthorized, 400 Bad Request)
            msg = f"chakoshi returned {e.response.status_code}: {e.response.text}"
            return [types.TextContent(type="text", text=msg)]

        except Exception as e:
            # Handle other unexpected errors (e.g., network issues, internal errors)
            return [types.TextContent(type="text", text=f"Unexpected error: {e}")]

    # Function to run the server using standard input/output.
    def run_stdio():
        """Runs the MCP server using stdio streams."""
        async def _runner():
            async with stdio_server() as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
        anyio.run(_runner)

    app.run_stdio = run_stdio
    return app
