# 🧠 AI Agent Toolkit

> A minimal, readable **autonomous AI agent** in ~100 lines of Python: Claude decides which tools to call, runs them, observes the results, and loops until the task is done.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tool Use](https://img.shields.io/badge/Pattern-Tool%20Use%20Loop-6366f1)
![Anthropic](https://img.shields.io/badge/Powered%20by-Claude-D97757)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ What it does

Give the agent a goal in plain language. It plans, calls tools, and returns a final answer:

```text
$ python agent.py "What is 15% of 2,480, then save the result in result.txt"

[step 1] calculator({'expression': '2480 * 0.15'}) -> 372.0
[step 2] write_file({'filename': 'result.txt', 'content': '372.0'}) -> Wrote 5 characters to result.txt

Final answer:
15% of 2,480 is 372. I saved it in result.txt.
```

## 🧰 Built-in tools

| Tool | Description |
|------|-------------|
| `calculator` | Safe arithmetic (AST-based, **no `eval`**) |
| `current_time` | Current date and time |
| `list_files` / `read_file` / `write_file` | Sandboxed file access inside `workspace/` |

## 🔄 How the agent loop works

```
        ┌──────────────────────────────────────────┐
        │  user task                               │
        ▼                                          │
   Claude thinks ──► needs a tool? ──yes──► run tool ──► feed result back
        │                                                    │
        no                                                   │
        ▼                                                    │
   final answer ◄────────────── (max 10 steps) ◄─────────────┘
```

## 🔒 Safety design

- **Sandboxed files** – paths are resolved and blocked if they escape `workspace/`.
- **No code execution** – the calculator parses an AST instead of calling `eval`.
- **Step limit** – the loop stops after 10 iterations to avoid runaway costs.
- **Errors are returned to the model** (`is_error`) so it can recover instead of crashing.

## 🚀 Quick start

```bash
git clone https://github.com/latouimouhamedbassim-create/ai-agent-toolkit.git
cd ai-agent-toolkit

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # add your ANTHROPIC_API_KEY
python agent.py "List my files and tell me the time"
```

## ➕ Add your own tool

1. Write a Python function in `tools.py`.
2. Add its JSON schema to `TOOLS`.
3. Register it in `REGISTRY`.

That's it – the agent will start using it when relevant. Ideas: web search, send email, query a database, create calendar events.

## 🛣️ Roadmap

- [ ] Web search tool
- [ ] Long-term memory
- [ ] Multi-agent workflow (planner + executor)
- [ ] Simple web dashboard for runs

## 👤 Author

**Mouhamed Bassim Latoui** – AI Developer (chatbots, agents, websites) · Constantine, Algeria
GitHub: [@latouimouhamedbassim-create](https://github.com/latouimouhamedbassim-create)

## 📄 License

MIT – free to use and adapt.
