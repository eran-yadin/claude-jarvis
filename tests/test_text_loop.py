"""Offline check of the job 1 path with a fake model: no API key, no cost.

Run: uv run python -m tests.test_text_loop
"""
import asyncio
import os
import threading
import time

os.environ["JARVIS_TOKEN"] = "test-token"

import uvicorn
import websockets

from brain import agent as agent_mod
from brain import main as main_mod
from brain.llm import LLMReply


class FakeLLM:
    """Asks for get_time once, then answers with what the tool returned."""
    def chat(self, system, messages, tools):
        last = messages[-1]["content"]
        if isinstance(last, list) and last and last[0].get("type") == "tool_result":
            return LLMReply(text=f"It is {last[0]['content']}.", raw_content=[{"type": "text", "text": "ok"}])
        return LLMReply(tool_calls=[{"id": "t1", "name": "get_time", "input": {}}],
                        raw_content=[{"type": "tool_use", "id": "t1", "name": "get_time", "input": {}}])


main_mod.JARVIS_TOKEN = "test-token"
main_mod.Agent = lambda: agent_mod.Agent(llm=FakeLLM())


async def check():
    url = "ws://127.0.0.1:8799/ws"
    async with websockets.connect(url, additional_headers={"Authorization": "Bearer test-token"}) as c:
        await c.send("what time is it")
        reply = await c.recv()
        assert reply.startswith("It is "), reply
        print("tool path OK:", reply)
    async with websockets.connect(url, additional_headers={"Authorization": "Bearer wrong"}) as c:
        try:
            await c.recv()
            raise AssertionError("bad token was accepted")
        except websockets.ConnectionClosed as e:
            assert e.rcvd.code == 4401, e.rcvd
            print("bad token rejected OK (4401)")


server = uvicorn.Server(uvicorn.Config(main_mod.app, host="127.0.0.1", port=8799, log_level="warning"))
threading.Thread(target=server.run, daemon=True).start()
while not server.started:
    time.sleep(0.05)
asyncio.run(check())
server.should_exit = True
print("ALL OK")
