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


def _build_server_params() -> StdioServerParameters:
    """Build common StdioServerParameters for tests."""
    return StdioServerParameters(
        command="uv",
        args=[
            "run",
            "main.py",
        ],
        env={
            "CHAKOSHI_API_KEY": os.environ.get("CHAKOSHI_API_KEY"),
            "CHAKOSHI_GUARDRAIL_ID": os.environ.get("CHAKOSHI_GUARDRAIL_ID"),
        },
    )


@pytest.mark.asyncio
async def test_mcp_get_list_stdio() -> None:
    """Verify that the list of MCP tools can be retrieved."""
    server_params = _build_server_params()

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
    """Verify the moderate_text tool with the Guardrails Apply API."""
    server_params = _build_server_params()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=None) as session:
            # Initialize the connection
            await session.initialize()

            # Call moderate_text tool
            result = await session.call_tool(
                "moderate_text", {"text": "お前はバカだな"}
            )

            # Parse the assessments response
            assessments = json.loads(result.content[0].text)
            # assessments should contain guardrails, user_input, and guardrails_result
            assert "guardrails" in assessments
            assert "user_input" in assessments
            assert "guardrails_result" in assessments
