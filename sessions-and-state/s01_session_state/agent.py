"""Tier 1 — Session state: short-term memory, scoped to one conversation."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

load_dotenv()

MODEL = "gemini-2.5-flash"


def remember(fact: str, tool_context: ToolContext) -> dict:
    """Save one short fact about the user, e.g. 'name is Mesh' or 'prefers concise answers'."""
    # tool_context is injected by ADK, not the model — it never appears in the tool schema.
    facts = tool_context.state.get("facts", [])
    facts.append(fact)
    tool_context.state["facts"] = facts
    return {"status": "saved", "facts_so_far": len(facts)}


root_agent = LlmAgent(
    name="assistant_that_remembers",
    model=MODEL,
    instruction=(
        "You are a helpful assistant.\n"
        "Whenever the user shares something about themselves (name, preferences, goals), "
        "call remember() to store it as one short fact, then continue normally.\n"
        "Use the known facts to personalize your answers.\n\n"
        "Facts you know about the user so far (may be empty):\n{facts?}"
    ),
    tools=[remember],
)
