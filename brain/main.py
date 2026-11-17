"""Brain service: one WebSocket, text in, text out.

Run: uv run uvicorn brain.main:app --host 127.0.0.1 --port 8765
"""
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .agent import Agent
from .config import JARVIS_TOKEN

logging.basicConfig(level=logging.INFO)
app = FastAPI()


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    # TODO 1: read the token the client sent (query param or first message),
    #         compare with JARVIS_TOKEN using secrets.compare_digest,
    #         close with code 4401 if it is wrong or JARVIS_TOKEN is empty
    await websocket.accept()
    agent = Agent()   # one conversation per connection
    try:
        while True:
            text = await websocket.receive_text()
            # TODO 2: agent.handle() blocks - run it off the event loop
            #         hint: await asyncio.to_thread(agent.handle, text)
            # TODO 3: send the reply back with websocket.send_text(...)
    except WebSocketDisconnect:
        pass
