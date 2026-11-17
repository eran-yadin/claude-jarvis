"""The model behind one small interface.

Why: agent.py should not know which provider it is talking to. Swapping
Claude for a local model later = a second class here + one line in config.yaml.
"""
from dataclasses import dataclass, field

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
        # TODO: create the anthropic client with ANTHROPIC_API_KEY
        # hint: anthropic.Anthropic(api_key=...)
        self.model = CONFIG["llm"]["model"]
        self.max_tokens = CONFIG["llm"]["max_tokens"]

    def chat(self, system: str, messages: list, tools: list) -> LLMReply:
        # TODO: one call to client.messages.create(model, max_tokens, system, messages, tools)
        # TODO: walk response.content:
        #         block.type == "text"     -> add to reply.text
        #         block.type == "tool_use" -> add {"id", "name", "input"} to reply.tool_calls
        # TODO: copy response.usage.input_tokens / output_tokens into the reply
        raise NotImplementedError


def get_llm():
    provider = CONFIG["llm"]["provider"]
    if provider == "anthropic":
        return AnthropicLLM()
    raise ValueError(f"unknown llm provider: {provider}")
