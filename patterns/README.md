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

---

## Pattern 2 — Sequential (`p02_sequential/`)

**What it is.** A pipeline: specialized agents run in a fixed order, and each one's output becomes the next one's input. The flow is decided by *you*, in code — no model chooses what runs next. Use it when the steps are always the same (draft → review → polish, extract → validate → format) and each step deserves its own focused prompt instead of one bloated mega-prompt.

**The example.** A customer-support pipeline: a **triager** classifies the message (JSON: category, urgency, sentiment), a **drafter** writes a reply that adapts to that triage (angry customer → apologize first), and a **tone checker** does a final quality pass. Three genuinely different jobs — classification, conditional writing, quality control — each with its own tight prompt.

**How state passing works.** This pattern's key mechanic. The triager has `output_key="triage"`, which saves its reply into *session state* — a shared dict all agents in the run can see. The drafter's instruction contains the placeholder `{triage}`, which ADK fills in from that state right before calling the model. That `output_key` → `{placeholder}` pipe is how data moves between agents in ADK. Note every instruction ends with "Output ONLY..." — in a pipeline each output is consumed raw by the next stage, so meta-commentary ("Here are three options...") breaks things.

**Try it.** Run `adk web`, pick `p02_sequential`, and send *"I've been charged twice this month and nobody answers my emails. This is unacceptable."* Then in a new session try *"Hey, how do I export my data to CSV?"* Same pipeline both times, but compare the triage JSON in the trace and watch the drafter's tone shift because of it.

---

## Pattern 3 — Parallel (`p03_parallel/`)

**What it is.** Independent sub-agents work on sub-tasks *at the same time*, then a final agent gathers and merges their results. Use it when the branches genuinely don't need each other's output — researching N topics, reviewing something from N angles, querying N sources. Wall-clock time drops to the slowest branch instead of the sum of all of them.

**The example.** A debate: an **optimist** lists the strongest arguments for the user's idea while a **skeptic** lists the strongest against — simultaneously, in isolation. A **synthesizer** then reads both and delivers a balanced verdict.

**The key mechanic.** `ParallelAgent` runs its sub-agents concurrently, each writing to its own `output_key` (`pros`, `cons`). But parallel branches alone can't produce one answer — so the fan-out is wrapped in a `SequentialAgent` whose last step reads *both* keys (`{pros}`, `{cons}`) and merges them. This fan-out → gather shape is how virtually every parallel flow ends up looking, and it shows patterns are composable: Parallel nests inside Sequential.

**Why isolation matters.** Because neither debater sees the other's arguments, you get two genuinely independent perspectives — the skeptic can't be swayed by the optimist. That's often the *reason* to go parallel, not just the speed.

**Try it.** Run `adk web`, pick `p03_parallel`, and ask *"Should I quit my job to go all-in on my side project?"* In the trace, note that the optimist and skeptic requests fire at the same time, and check the synthesizer's request to see both lists injected where `{pros}` and `{cons}` were.

---

## Pattern 4 — Loop & Critique (`p04_loop_critique/`)

**What it is.** A generator produces output; a critic judges it against explicit criteria. Fail → the feedback goes back to the generator and it tries again. Pass → the critic stops the loop. A `max_iterations` cap guarantees it always terminates. Use it when quality is checkable but hard to nail in one shot — and the criteria must be *concrete*: a critic told "make it better" loops forever.

**The example.** A **generator** writes a product tagline; a strict **critic** checks it (under 8 words, memorable, no clichés). If the tagline passes, the critic calls the built-in `exit_loop` tool; otherwise it outputs one specific improvement, and the next round's generator has to address it.

**Two new mechanics.** First, **`exit_loop`** — the loop's exit is a *tool call*, which means the critic (a model) decides when the work is good enough, while `max_iterations=3` keeps a hard ceiling on cost. Second, the **optional placeholder `{feedback?}`** — on the very first pass no feedback exists in state yet; the trailing `?` tells ADK "fill with blank if missing" instead of crashing. State also *overwrites* each round: `tagline` and `feedback` always hold the latest version, which is exactly what a refinement loop wants.

**Try it.** Run `adk web`, pick `p04_loop_critique`, and describe a product: *"a coffee mug that keeps drinks hot for 6 hours"*. In the trace, count the generator→critic rounds — sometimes it passes on round one, sometimes you'll watch the critic reject, the feedback flow into the next generator prompt, and the tagline visibly improve. If it never passes, it stops at 3 rounds anyway.