"""A minimal autonomous AI agent: Claude + tools + a reasoning loop."""
import os
import sys

from dotenv import load_dotenv

from tools import REGISTRY, TOOLS

load_dotenv()

MODEL = os.getenv("MODEL", "claude-sonnet-4-5")
MAX_STEPS = 10
DEMO_TASK = "What is 15% of 2,480? Save the result in result.txt, then list my files."
SYSTEM = (
    "You are an autonomous assistant. Break the task into steps, use the tools when "
    "they help, and give a clear final answer. Never guess a calculation: use the calculator."
)

# Demo mode: forced with --demo / DEMO_MODE=1, or automatic when no API key is set.
DEMO_MODE = "--demo" in sys.argv or os.getenv("DEMO_MODE") == "1" or not os.getenv("ANTHROPIC_API_KEY")
sys.argv = [a for a in sys.argv if a != "--demo"]

if DEMO_MODE:
    from demo_client import DemoClient

    client = DemoClient()
    print("[demo mode] scripted model, real tools - no API key used\n")
else:
    from anthropic import Anthropic

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
    task = " ".join(sys.argv[1:]) or (DEMO_TASK if DEMO_MODE else input("Task: "))
    print("\nFinal answer:\n" + run_agent(task))
