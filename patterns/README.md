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

---

## Pattern 5 — Coordinator (`p05_coordinator/`)

**What it is.** A central agent reads the request and *decides at runtime* which specialist should handle it. This is the first pattern where control flow is a model decision, not code: Sequential/Parallel/Loop wire the flow in advance, the Coordinator picks a route per request. Use it when requests are heterogeneous and you can't know the path up front (support desk: billing vs bug vs how-to).

**The example.** A tutoring receptionist with two specialists: a **math tutor** and a **writing tutor**. Ask a math question, the coordinator hands you to the math tutor; send a broken sentence, you land with the writing tutor.

**The key mechanic.** Putting agents in `sub_agents` gives the coordinator a built-in `transfer_to_agent` tool. When it calls that tool, the conversation is *handed over* — the specialist talks to the user directly from then on; the coordinator is out of the picture. Routing runs on each specialist's **`description`** field, which makes descriptions load-bearing prompt text, not documentation. Vague descriptions → misroutes.

**The tradeoff to notice.** Routing is probabilistic. The same request can route differently on different runs, and a request that fits neither specialist tests how well the coordinator's instruction holds ("don't answer yourself"). That flexibility-vs-predictability trade against Sequential is the core lesson.

**Try it.** Run `adk web`, pick `p05_coordinator`, and send *"what is 15% of 240?"* — in the trace you'll see the coordinator call `transfer_to_agent(agent_name='math_tutor')` before the tutor answers. New session, send *"can you fix this sentence: 'me and him goes to store yesterday'"* and watch it route the other way. Then probe the edge: *"what should I cook tonight?"* — neither specialist fits; does it stay a receptionist or try to be a chef?

---

## Pattern 6 — Agent-as-Tool (`p06_agent_as_tool/`)

**What it is.** A sub-agent wrapped so the parent can call it *like a function*: parent sends input, sub-agent returns its answer, parent keeps reasoning with the result. The direct contrast with the Coordinator is the whole point — **delegation transfers control** (the specialist takes over the conversation), **invocation keeps it** (the specialist answers the parent, never the user). Use it when the parent needs a specialist's *answer* mid-task, not a hand-off.

**The example.** A **report writer** turns raw notes into a two-line status update. Line 1 comes from calling the **summarizer** agent as a tool; line 2 (the recommended next step) the parent decides itself — proof it's still in charge after the tool call.

**The key mechanic.** `AgentTool(agent=summarizer)` in the parent's `tools` list. To the parent it looks exactly like `add()` did in pattern 1 — the difference is the "function body" is a whole model run. Two consequences worth noticing: the sub-agent only sees what's passed in as the tool argument (a context boundary — its own conversation, its own window), and its multi-step work collapses to a single result in the parent's context. That makes this the cleanest way to isolate a noisy sub-task.

**Try it.** Run `adk web`, pick `p06_agent_as_tool`, and paste some messy notes: *"demo went well, latency 4s felt slow, 2 of 5 testers hit a login bug, everyone liked the new UI, marketing wants a launch date by Friday."* In the trace you'll see the parent call the `summarizer` tool, the summarizer's own model run nested inside it, and then — unlike pattern 5 — the **parent** produce the final answer. Compare the traces side by side: transfer ends with the specialist talking; agent-as-tool ends with the parent talking.