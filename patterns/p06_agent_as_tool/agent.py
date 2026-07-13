"""Pattern 06 — Agent-as-Tool: a sub-agent wrapped as a callable tool; the parent keeps control."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

load_dotenv()

MODEL = "gemini-2.5-flash"

summarizer = LlmAgent(
    name="summarizer",
    model=MODEL,
    # As with the coordinator's specialists, the description is what the
    # parent model reads when deciding whether to call this tool.
    description="Summarizes any text into exactly one sentence.",
    instruction="Summarize the given text in exactly one sentence. Output ONLY that sentence.",
)

# AgentTool wraps the summarizer as a callable tool. Unlike the Coordinator's
# transfer (pattern 05), the parent gets the result back and keeps reasoning —
# control never leaves the parent.
root_agent = LlmAgent(
    name="report_writer",
    model=MODEL,
    instruction=(
        "Turn the user's raw notes into a status update with exactly two lines:\n"
        "1. TL;DR: — use the summarizer tool to condense the notes, and use its result here.\n"
        "2. Next step: — one concrete recommended action, decided by you.\n"
        "Output ONLY those two lines."
    ),
    tools=[AgentTool(agent=summarizer)],
)
