#!/usr/bin/env python3
"""
End-to-end test: launch the server as Claude Desktop would (python -m bibliomantic_server)
and drive it over the MCP stdio protocol with the official client.
"""

import asyncio
import os
import re
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).parent


def _text(result) -> str:
    return "".join(block.text for block in result.content if hasattr(block, "text"))


async def _exercise_server():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "bibliomantic_server"],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            assert init.server_info.name == "Enhanced Bibliomantic Oracle"

            tools = {tool.name for tool in (await session.list_tools()).tools}
            assert tools == {"i_ching_divination", "bibliomantic_consultation", "get_hexagram_details", "server_statistics"}
            assert {str(r.uri) for r in (await session.list_resources()).resources} == {"iching://database"}
            assert [t.uri_template for t in (await session.list_resource_templates()).resource_templates] == ["hexagram://{number}"]
            assert {p.name for p in (await session.list_prompts()).prompts} == {
                "career_guidance_prompt", "creative_guidance_prompt", "general_guidance_prompt"}

            stats = _text(await session.call_tool("server_statistics", {}))
            assert "2024-11-05" not in stats and "all 64 with Chinese names" not in stats
            assert re.search(r"judgment and image texts: \d+ of 64", stats), stats

            details = _text(await session.call_tool("get_hexagram_details", {"hexagram_number": 1}))
            assert "乾 ☰☰" in details
            assert "between 1 and 64" in _text(await session.call_tool("get_hexagram_details", {"hexagram_number": 65}))

            assert "Hexagram" in _text(await session.call_tool("i_ching_divination", {}))
            assert "Please provide a question" in _text(await session.call_tool("bibliomantic_consultation", {"query": " "}))

            # Cast until a reading has changing lines (P(no changing lines) ≈ 0.18 per cast)
            for _ in range(25):
                consultation = _text(await session.call_tool("bibliomantic_consultation", {"query": "a career question"}))
                assert "Line 1: Line 1" not in consultation and not re.search(r"Line (\d): Line \1", consultation)
                if "**Changing Lines:**" in consultation:
                    assert "**Resulting Situation" in consultation
                    break
            else:
                pytest.fail("no reading with changing lines in 25 casts")

            database = (await session.read_resource("iching://database")).contents[0].text
            assert re.search(r"judgment and image texts: \d+ of 64", database)
            assert "Hexagram 11: Peace" in (await session.read_resource("hexagram://11")).contents[0].text
            prompt = await session.get_prompt("career_guidance_prompt", {"situation": "a test"})
            assert len(prompt.messages) == 1


def test_server_over_stdio():
    asyncio.run(_exercise_server())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
