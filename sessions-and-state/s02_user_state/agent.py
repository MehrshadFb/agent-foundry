"""Tier 2 — User state: persistent memory, shared across all of a user's sessions."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

load_dotenv()

MODEL = "gemini-2.5-flash"


def remember(fact: str, tool_context: ToolContext) -> dict:
    """Save one short fact about the user, e.g. 'name is Mesh' or 'prefers concise answers'."""
    # Identical to tier 1 except the key prefix: "user:" scopes the value to the
    # user_id instead of the session, so every session of this user sees it.
    facts = tool_context.state.get("user:facts", [])
    facts.append(fact)
    tool_context.state["user:facts"] = facts
    return {"status": "saved", "facts_so_far": len(facts)}


root_agent = LlmAgent(
    name="assistant_that_never_forgets",
    model=MODEL,
    instruction=(
        "You are a helpful assistant.\n"
        "Whenever the user shares something about themselves (name, preferences, goals), "
        "call remember() to store it as one short fact, then continue normally.\n"
        "Use the known facts to personalize your answers.\n\n"
        "Facts you know about the user so far (may be empty):\n{user:facts?}"
    ),
    tools=[remember],
)
