# Agent design patterns

There are only a handful of ways to structure AI agents, and almost every agent system is built from them. This folder is where I learn those patterns hands-on — the six core ones from Google's ADK taxonomy — by building a tiny, runnable example for each, one at a time.

The six patterns, in learning order:


| #   | Pattern             | Idea in one line                                              |
| --- | ------------------- | ------------------------------------------------------------- |
| 1   | **Single**          | One agent with tools does the whole job                       |
| 2   | **Sequential**      | Agents run in a fixed order, output feeding the next          |
| 3   | **Parallel**        | Sub-agents work simultaneously, results get merged            |
| 4   | **Loop & Critique** | Generator + critic loop until the output is good enough       |
| 5   | **Coordinator**     | A router agent hands the request to the right specialist      |
| 6   | **Agent-as-Tool**   | An agent calls another agent like a function, keeping control |


Every pattern folder has just two files: `agent.py` (defines `root_agent` — the actual example) and `__init__.py` (one line of plumbing so ADK can import it). Folder names use `p01_`-style prefixes because ADK requires valid Python identifiers.

**To run any pattern** — from this folder, with `GOOGLE_API_KEY` set in the repo-root `.env`:

```bash
adk web                 # dev UI with step-by-step traces — best for learning
adk run p01_single      # or chat in the terminal
```

---



## Pattern 1 — Single (`p01_single/`)

**What it is.** One agent, several tools. The model runs a loop: read the request → decide if a tool is needed → call it → look at the result → repeat until it can answer. This is the default pattern — start here, and only go multi-agent when one agent demonstrably struggles (too many tools, context getting too long, steps needing different personas).

**The example.** A calculator agent with two tools, `add(a, b)` and `multiply(a, b)`. The tools are deliberately trivial — the point isn't the math (Gemini can add without help), it's watching the tool-use loop. The instruction says "never do math in your head" precisely to force tool calls so you can see them.

**How tools work.** A tool is just a Python function with type hints and a docstring. ADK converts that signature into a schema the model can see; when the model wants to use it, ADK runs the real function and feeds the result back. Same mechanics whether the tool adds two numbers or queries a database.

**Try it.** Run `adk web`, pick `p01_single`, and ask *"what is (3 + 4) * 5?"*. In the trace view you'll see the model call `add(3, 4)`, get `7`, call `multiply(7, 5)`, get `35`, and only then write its answer — two tool calls it chained on its own, without being told the order.