# Sessions & state

An LLM is stateless — every request starts from zero, and "memory" is whatever you put back into the prompt. ADK's answer is the **session**: a record of one conversation, holding its events (every message and tool call) and its **state** — a dict that agents and tools can read and write. This folder works through the three tiers of that memory, from shortest-lived to longest, one example each.

| Tier | Scope | Survives | ADK mechanism |
|------|-------|----------|---------------|
| 1. Session state | one conversation | until the session ends | `tool_context.state`, `output_key`, `{placeholders}` |
| 2. User state | all sessions of one user | across sessions | `user:` key prefix + a persistent session service |
| 3. Memory | past conversations | indefinitely | `MemoryService` + recall tools |

Run from this folder: `adk web`, then pick the example.

---

## Tier 1 — Session state (`s01_session_state/`)

**What it is.** The scratchpad of a single conversation. We've already used it in the patterns — `output_key` writes to it, `{placeholders}` read from it. The new piece here: **tools can read and write it too**, which turns state from a pipe between agents into working memory the model controls.

**The example.** An assistant with one tool, `remember(fact)`. When you mention something about yourself, the model calls the tool; the tool appends the fact to `state["facts"]`; and from the next turn on, the instruction placeholder `{facts?}` injects everything it knows back into the prompt. The model decides *what* is worth remembering — the state mechanics just store it.

**The key mechanic: `ToolContext`.** Add a `tool_context: ToolContext` parameter to any tool and ADK injects it automatically — the model never sees that parameter in the tool's schema (check the trace: the tool takes only `fact`). Through it, tools reach `tool_context.state`. One rule: state only persists via *assignment* — `state["facts"] = facts` — which is why the tool reads the list, appends, and writes it back instead of mutating in place.

**The limit (which motivates tier 2).** All of this lives in one session. Open a new session and the assistant knows nothing again — session state is short-term by design.

**Try it.** Run `adk web`, pick `s01_session_state`, and say *"I'm Mesh, I'm learning agent engineering, and I like short answers."* Watch the trace: two or three `remember()` calls, and the State chip updating. Ask *"what should I build this weekend?"* — the answer should use what it knows. Then click **+ New Session** and ask *"what's my name?"* — gone. That's tier 1's boundary.

---

## Tier 2 — User state (`s02_user_state/`)

**What it is.** State that belongs to the *user*, not the conversation. The code is tier 1's assistant with exactly one change: the state key is `"user:facts"` instead of `"facts"`. That prefix changes the scope — every session with the same `user_id` reads and writes the same value, so what the assistant learns in one conversation is already known in the next.

**The key mechanic: prefixes.** A state key's prefix decides its lifetime:

| Key | Scope |
|-----|-------|
| `facts` | this session only (tier 1) |
| `user:facts` | all sessions of this user |
| `app:facts` | all sessions of *all* users |
| `temp:facts` | this turn only, never saved |

Prefixed keys work everywhere plain ones do — `tool_context.state["user:facts"]` in tools, `{user:facts?}` in instructions.

**One dependency to understand.** "Persistent" is only as persistent as the *session service* storing it. `adk web` keeps sessions in a local SQLite file (`.adk/session.db`, gitignored), so user state survives new sessions and even restarts. In-memory services lose everything on process exit; production setups point at a real database. The prefix sets the scope — the service sets the durability.

**Try it.** Run `adk web`, pick `s02_user_state`, and introduce yourself like in tier 1. Then click **+ New Session** and ask *"what's my name?"* — this time it knows. That one-line diff (`facts` → `user:facts`) is the entire difference between tiers 1 and 2.
