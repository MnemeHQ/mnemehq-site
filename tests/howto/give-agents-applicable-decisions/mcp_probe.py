"""Call Mneme's decision-mcp server over stdio, the way an MCP host does.

Usage:
    python mcp_probe.py list
    python mcp_probe.py <tool-name> '<json arguments>'
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command="mneme",
    args=["decision-mcp", "--proposals", "", "--adr-dir", os.environ.get("ADR_DIR", "docs/adr")],
)


async def main(tool: str, arguments: str) -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if tool == "list":
                tools = await session.list_tools()
                print("\n".join(t.name for t in tools.tools))
                return
            result = await session.call_tool(tool, json.loads(arguments))
            for block in result.content:
                print(json.dumps(json.loads(block.text), indent=2, sort_keys=True))


asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "{}"))
