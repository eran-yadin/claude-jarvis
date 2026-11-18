"""The tool loop: text in -> (model <-> tools) -> text out."""
import logging

from .config import CONFIG
from .llm import get_llm
from .tools import TOOL_SCHEMAS, run_tool

log = logging.getLogger("jarvis.agent")

SYSTEM_PROMPT = """You are Jarvis, a voice assistant. Your replies are spoken aloud:
keep them short, plain sentences, no markdown, no lists."""

MAX_STEPS = CONFIG["llm"]["max_steps"]


class Agent:
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.messages: list = []   # conversation history for this session

    def handle(self, user_text: str) -> str:
        """One spoken command in, one reply to speak out."""
        self.messages.append({"role": "user", "content": user_text})
        for step in range(1, MAX_STEPS + 1):
            reply = self.llm.chat(SYSTEM_PROMPT, self.messages, TOOL_SCHEMAS)
            log.info("step %d: %d in / %d out tokens, %d tool call(s)",
                     step, reply.input_tokens, reply.output_tokens, len(reply.tool_calls))
            self.messages.append({"role": "assistant", "content": reply.raw_content})
            if not reply.tool_calls:
                return reply.text or "Done."
            results = []
            for call in reply.tool_calls:
                output = run_tool(call["name"], call["input"])
                log.info("tool %s -> %s", call["name"], output[:200])
                results.append({"type": "tool_result", "tool_use_id": call["id"], "content": output})
            self.messages.append({"role": "user", "content": results})
        log.warning("hit max_steps (%d)", MAX_STEPS)
        # history ends on tool results; close the turn so the next command starts clean
        self.messages.append({"role": "assistant", "content": "I stopped there, it took too many steps."})
        return "Sorry, that took too many steps, so I stopped."
