"""Job 1 client: type a line, print Jarvis's answer. Voice replaces this in job 3.

Run: uv run python -m client.terminal
"""
import asyncio
import os
import sys
from pathlib import Path

import websockets
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "jarvis-data" / "secrets.env")

BRAIN_URL = os.environ.get("JARVIS_BRAIN_URL", "ws://127.0.0.1:8765/ws")
TOKEN = os.environ.get("JARVIS_TOKEN", "")


async def main():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        async with websockets.connect(BRAIN_URL, additional_headers=headers) as conn:
            print("connected to Jarvis. empty line or Ctrl-C to quit.")
            while True:
                line = (await asyncio.to_thread(input, "you> ")).strip()
                if not line:
                    break
                await conn.send(line)
                print("jarvis>", await conn.recv())
    except websockets.ConnectionClosed as e:
        sys.exit(f"brain closed the connection: {e.rcvd.code if e.rcvd else ''} {e.rcvd.reason if e.rcvd else ''}")
    except OSError as e:
        sys.exit(f"can't reach the brain at {BRAIN_URL}: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print()
