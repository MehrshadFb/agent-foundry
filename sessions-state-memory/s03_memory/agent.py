"""Tier 3 — Memory: a searchable archive of past conversations, recalled on demand."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext, load_memory

load_dotenv()

MODEL = "gemini-2.5-flash"


async def archive_conversation(tool_context: ToolContext) -> dict:
    """Save the current conversation to long-term memory so future sessions can recall it."""
    # Hands the whole session (all events so far) to the memory service.
    await tool_context.add_session_to_memory()
    return {"status": "archived"}


root_agent = LlmAgent(
    name="assistant_with_recall",
    model=MODEL,
    instruction=(
        "You are a helpful assistant.\n"
        "When the user asks you to remember or save this conversation, call "
        "archive_conversation.\n"
        "When the user asks about something from a past conversation, call "
        "load_memory with a short search query, then answer from what it returns.\n"
        "If memory has nothing relevant, say so honestly."
    ),
    tools=[archive_conversation, load_memory],  # load_memory is a prebuilt ADK tool
)
