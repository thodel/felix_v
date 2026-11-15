"""Minimal synchronous wrapper around the MCP streamable-HTTP client for the tei MCP fleet.

URLs and headers come from the user's Claude config (~/.claude.json, mcpServers), read at runtime;
nothing secret is written anywhere. Results are cached on disk by (server, tool, args).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client


def _servers() -> dict:
    d = json.loads(Path(os.path.expanduser("~/.claude.json")).read_text())
    found = {}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "mcpServers" and isinstance(v, dict):
                    found.update(v)
                else:
                    walk(v)
    walk(d)
    return found


class MCP:
    def __init__(self, cache: Path):
        self.cfg = _servers()
        self.cache_dir = cache
        cache.mkdir(parents=True, exist_ok=True)

    def call(self, server: str, tool: str, **args):
        h = hashlib.sha1(json.dumps([server, tool, args], sort_keys=True).encode()).hexdigest()
        f = self.cache_dir / f"{h}.json"
        if f.exists():
            return json.loads(f.read_text())
        res = asyncio.run(self._call(server, tool, args))
        f.write_text(json.dumps(res, ensure_ascii=False))
        return res

    async def _call(self, server, tool, args):
        s = self.cfg[server]
        client = create_mcp_http_client(headers=s.get("headers") or None)
        async with client, streamable_http_client(s["url"], http_client=client) as streams:
            r, w = streams[0], streams[1]
            async with ClientSession(r, w) as sess:
                await sess.initialize()
                out = await sess.call_tool(tool, args)
                sc = getattr(out, "structured_content", None) or getattr(out, "structuredContent", None)
                if sc:
                    return sc.get("result", sc) if isinstance(sc, dict) else sc
                texts = [c.text for c in out.content if getattr(c, "type", "") == "text"]
                try:
                    j = json.loads(texts[0]) if texts else None
                    return j.get("result", j) if isinstance(j, dict) else j
                except (json.JSONDecodeError, IndexError):
                    return texts
