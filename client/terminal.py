"""Job 1 client: type a line, print Jarvis's answer. Voice replaces this in job 3.

Run: uv run python -m client.terminal
"""
import asyncio
import os
from pathlib import Path

import websockets
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "jarvis-data" / "secrets.env")

BRAIN_URL = os.environ.get("JARVIS_BRAIN_URL", "ws://127.0.0.1:8765/ws")
TOKEN = os.environ.get("JARVIS_TOKEN", "")


async def main():
    # TODO 1: connect with websockets.connect(BRAIN_URL ...) and pass TOKEN
    #         the same way brain/main.py expects it
    # TODO 2: loop: read a line (hint: await asyncio.to_thread(input, "you> ")),
    #         send it, await the reply, print it. empty line or Ctrl-C quits.
    raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(main())
