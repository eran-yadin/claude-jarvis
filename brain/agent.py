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
    def __init__(self):
        self.llm = get_llm()
        self.messages: list = []   # conversation history for this session

    def handle(self, user_text: str) -> str:
        """One spoken command in, one reply to speak out."""
        # TODO 1: append {"role": "user", "content": user_text} to self.messages
        # TODO 2: loop at most MAX_STEPS times:
        #           reply = self.llm.chat(SYSTEM_PROMPT, self.messages, TOOL_SCHEMAS)
        #           log reply.input_tokens / reply.output_tokens  (cost per call)
        #           append the assistant turn (reply.raw_content) to self.messages
        #           no tool calls -> return reply.text
        #           else run each with run_tool(name, input) and append ONE user turn
        #                holding a {"type": "tool_result", "tool_use_id", "content"} per call
        # TODO 3: if the loop runs out, return a short "that took too many steps" message
        raise NotImplementedError
