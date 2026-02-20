import asyncio
import os

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def main():
    # Start the MCP server as a subprocess and communicate via stdio
    server = StdioServerParameters(
        command="/usr/local/bin/python",
        args=["-m", "mcp_server.server"],
        env={
            # IMPORTANT inside docker: call FastAPI via service name
            "API_BASE": os.getenv("API_BASE", "http://api:8000")
        },
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            res = await session.call_tool(
                "recommend_journey",
                {
                    "line_id": "piccadilly",
                    "from_": "2026-01-20T00:00:00Z",
                    "to": "2026-02-21T23:59:59Z",
                },
            )

            for c in res.content:
                if getattr(c, "text", None):
                    print(c.text)


if __name__ == "__main__":
    asyncio.run(main())