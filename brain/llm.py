"""The model behind one small interface.

Why: agent.py should not know which provider it is talking to. Swapping
Claude for a local model later = a second class here + one line in config.yaml.
"""
from dataclasses import dataclass, field

import anthropic

from .config import ANTHROPIC_API_KEY, CONFIG


@dataclass
class LLMReply:
    text: str = ""                                   # what to say, if anything
    tool_calls: list = field(default_factory=list)   # [{"id", "name", "input"}]
    raw_content: list = field(default_factory=list)  # provider blocks, to append to history
    input_tokens: int = 0
    output_tokens: int = 0


class AnthropicLLM:
    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is empty - put it in jarvis-data/secrets.env")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CONFIG["llm"]["model"]
        self.max_tokens = CONFIG["llm"]["max_tokens"]

    def chat(self, system: str, messages: list, tools: list) -> LLMReply:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        )
        reply = LLMReply(raw_content=list(response.content))
        texts = []
        for block in response.content:
            if block.type == "text":
                texts.append(block.text)
            elif block.type == "tool_use":
                reply.tool_calls.append({"id": block.id, "name": block.name, "input": block.input})
        reply.text = " ".join(t.strip() for t in texts if t.strip())
        reply.input_tokens = response.usage.input_tokens
        reply.output_tokens = response.usage.output_tokens
        return reply


def get_llm():
    provider = CONFIG["llm"]["provider"]
    if provider == "anthropic":
        return AnthropicLLM()
    raise ValueError(f"unknown llm provider: {provider}")
