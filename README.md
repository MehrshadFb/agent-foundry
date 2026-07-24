## Topics

- [x] **Design patterns** (`patterns/`) — the six ways to structure agents: single, sequential, parallel, loop & critique, coordinator, agent-as-tool
- [x] **Sessions, state & memory** (`sessions-state-memory/`) — how agents remember things: within one conversation, across conversations, and long-term recall

- [ ] **Callbacks & guardrails** — intercept requests before the model or a tool runs; block what shouldn't pass
- [ ] **MCP servers** — package tools so any agent or client can use them
- [ ] **Context engineering** — what goes into the model's window each step, and how to keep it from rotting
- [ ] **Tool design** — schemas, descriptions, and error messages a model can actually act on
- [ ] **Evals** — test agents: right answers (outcomes) and sensible steps (trajectories)
- [ ] **Observability & tracing** — see what agents did and why
- [ ] **Agent security** — prompt injection, least-privilege tools, sandboxing
- [ ] **Human-in-the-loop** — approval gates, interrupts, escalation
- [ ] **Memory architectures** — vector stores vs files vs graphs, beyond ADK's built-ins
- [ ] **Durable execution** — checkpointing, resuming after failure
- [ ] **Cost & latency** — caching, smaller models, knowing what each call costs
- [ ] **Agentic RAG** — retrieval the agent directs itself
- [ ] **Computer use / browser agents**
- [ ] **A2A protocol** — agents talking to other agents
- [ ] **Agent UX** — streaming progress, plan previews, building trust
- [ ] **LangGraph re-implementations** — redo the six patterns in LangGraph for comparison (parked for now)

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
```

Then from any topic folder: `adk web`