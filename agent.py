"""A minimal autonomous AI agent: Claude + tools + a reasoning loop."""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import REGISTRY, TOOLS

load_dotenv()

MODEL = os.getenv("MODEL", "claude-sonnet-4-5")
MAX_STEPS = 10
SYSTEM = (
    "You are an autonomous assistant. Break the task into steps, use the tools when "
    "they help, and give a clear final answer. Never guess a calculation: use the calculator."
)

client = Anthropic()


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    try:
        return str(REGISTRY[name](**args)), False
    except Exception as exc:
        return f"Error: {exc}", True


def run_agent(task: str, verbose: bool = True) -> str:
    messages = [{"role": "user", "content": task}]

    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        results = []
        for block in response.content:
            if block.type == "tool_use":
                output, is_error = run_tool(block.name, block.input)
                if verbose:
                    print(f"[step {step}] {block.name}({block.input}) -> {output[:120]}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})

    return "Stopped: step limit reached."


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or input("Task: ")
    print("\nFinal answer:\n" + run_agent(task))
