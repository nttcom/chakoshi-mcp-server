"""MCP functionality test.

You need to set up a conftest.py file.
Please run this from the project root.

uv run pytest -sv
"""

import json
import os
import pytest
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters


@pytest.mark.asyncio
async def test_mcp_get_list_stdio() -> None:
    """Verify that the list of MCP tools can be retrieved."""
    server_params = StdioServerParameters(
        command="uv",  # Executable
        args=[
            "run",
            "main.py",
        ],
        env={"CHAKOSHI_API_KEY": os.environ.get("CHAKOSHI_API_KEY")},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=None) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)
            assert tools


@pytest.mark.asyncio
async def test_mcp_call_moderate_text_stdio() -> None:
    """Verify the moderate_text tool."""
    server_params = StdioServerParameters(
        command="uv",  # Executable
        args=[
            "run",
            "main.py",
        ],
        env={"CHAKOSHI_API_KEY": os.environ.get("CHAKOSHI_API_KEY")},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=None) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            result = await session.call_tool(
                "moderate_text", {"text": "お前はバカだな"}
            )

            chakoshi_json = json.loads(result.content[0].text)
            assert chakoshi_json["label_str"] == "unsafe"
            assert chakoshi_json["unsafe_category"] == "harassment"
