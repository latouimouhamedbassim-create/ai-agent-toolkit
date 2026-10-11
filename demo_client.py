"""Keyless DEMO client: a scripted stand-in for the Anthropic client.

It plays the role of the *model* (it decides which tool to call), while the tools
and the agent loop are the REAL code from agent.py / tools.py. Nothing here is a
real model output: it exists so anyone can run the agent without an API key.
"""
from dataclasses import dataclass, field
from types import SimpleNamespace

PLAN = [
    ("calculator", {"expression": "2480 * 0.15"}),
    ("write_file", {"filename": "result.txt", "content": "15% of 2480 = {calc}"}),
    ("list_files", {}),
]


@dataclass
class _Response:
    content: list = field(default_factory=list)
    stop_reason: str = "end_turn"


def _text(text):
    return SimpleNamespace(type="text", text=text)


def _tool(i, name, args):
    return SimpleNamespace(type="tool_use", id=f"demo_{i}", name=name, input=args)


class _Messages:
    def create(self, *, messages, **_ignored):
        done = sum(1 for m in messages if m["role"] == "user" and isinstance(m["content"], list))
        if done < len(PLAN):
            name, args = PLAN[done]
            if name == "write_file":  # reuse the real calculator result from the previous step
                calc = messages[-1]["content"][0]["content"]
                args = {**args, "content": args["content"].format(calc=calc)}
            return _Response([_tool(done, name, args)], stop_reason="tool_use")
        files = messages[-1]["content"][0]["content"].replace("\n", ", ")
        return _Response([_text(
            "15% of 2,480 is 372. I saved the result in result.txt "
            f"(workspace now contains: {files}).")])


class DemoClient:
    messages = _Messages()
