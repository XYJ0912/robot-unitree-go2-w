"""Optional localhost-only end-to-end check; never persists the image."""

from __future__ import annotations

import asyncio
import base64
import json
import sys

from fastmcp import Client


async def main(port: int) -> None:
    async with Client(f"http://127.0.0.1:{port}/mcp", timeout=10) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools]
        if "snapshot" not in names:
            raise RuntimeError(f"snapshot tool absent: {names}")
        result = await client.call_tool("snapshot", {})
        if result.is_error:
            raise RuntimeError("snapshot tool returned an error")
        payload = result.structured_content
        if payload is None:
            payload = json.loads(result.content[0].text)
        if "result" in payload and isinstance(payload["result"], dict):
            payload = payload["result"]
        width, height = payload["width"], payload["height"]
        pixels = base64.b64decode(payload["data"], validate=True)
        if payload["encoding"] != "rgb8" or payload["step"] != width * 3:
            raise RuntimeError("unexpected image encoding or step")
        if len(pixels) != width * height * 3:
            raise RuntimeError("decoded RGB byte count does not match image dimensions")
        print({key: payload.get(key) for key in ("width", "height", "encoding", "step", "is_bigendian")})
        print("decoded_rgb_bytes:", len(pixels))


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1])))
