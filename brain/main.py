"""Brain service: one WebSocket, text in, text out.

Run: uv run uvicorn brain.main:app --host 127.0.0.1 --port 8765
Auth: the client sends "Authorization: Bearer <JARVIS_TOKEN>" on connect.
"""
import asyncio
import logging
import secrets

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .agent import Agent
from .config import JARVIS_TOKEN

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("jarvis.brain")
app = FastAPI()


def _token_ok(websocket: WebSocket) -> bool:
    if not JARVIS_TOKEN:
        return False   # no token configured = refuse everyone
    header = websocket.headers.get("authorization", "")
    sent = header.removeprefix("Bearer ").strip()
    return secrets.compare_digest(sent.encode(), JARVIS_TOKEN.encode())


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    if not _token_ok(websocket):
        log.warning("rejected connection from %s: bad or missing token", websocket.client)
        await websocket.close(code=4401, reason="unauthorized")
        return
    try:
        agent = Agent()   # one conversation per connection
    except Exception as e:
        log.error("could not start agent: %s", e)
        await websocket.send_text(f"Brain error: {e}")
        await websocket.close(code=1011)
        return
    try:
        while True:
            text = await websocket.receive_text()
            try:
                reply = await asyncio.to_thread(agent.handle, text)
            except Exception as e:
                log.exception("agent failed")
                reply = f"Sorry, something went wrong: {e}"
            await websocket.send_text(reply)
    except WebSocketDisconnect:
        pass
