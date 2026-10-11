"""Tools the agent can call. Each tool = a JSON schema + a Python function."""
import ast
import operator
from datetime import datetime
from pathlib import Path

WORKDIR = Path("workspace").resolve()
WORKDIR.mkdir(exist_ok=True)

# ---- safe calculator (no eval) ------------------------------------------------
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    return str(_eval(ast.parse(expression, mode="eval").body))


def current_time() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _safe_path(name: str) -> Path:
    path = (WORKDIR / name).resolve()
    if WORKDIR not in path.parents and path != WORKDIR:
        raise ValueError("Path escapes the workspace")
    return path


def read_file(filename: str) -> str:
    return _safe_path(filename).read_text(encoding="utf-8")[:10_000]


def write_file(filename: str, content: str) -> str:
    path = _safe_path(filename)
    path.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {filename}"


def list_files() -> str:
    return "\n".join(sorted(p.name for p in WORKDIR.iterdir())) or "(empty)"


TOOLS = [
    {"name": "calculator", "description": "Evaluate an arithmetic expression, e.g. '(12*3)/4'.",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "current_time", "description": "Get the current local date and time.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "list_files", "description": "List files in the agent's workspace folder.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "read_file", "description": "Read a text file from the workspace.",
     "input_schema": {"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}},
    {"name": "write_file", "description": "Create or overwrite a text file in the workspace.",
     "input_schema": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
                      "required": ["filename", "content"]}},
]

REGISTRY = {
    "calculator": calculator, "current_time": current_time, "list_files": list_files,
    "read_file": read_file, "write_file": write_file,
}
