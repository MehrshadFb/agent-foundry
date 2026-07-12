"""Pattern 05 — Coordinator: a central agent routes the request to a specialist at runtime."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()

MODEL = "gemini-2.5-flash"

math_tutor = LlmAgent(
    name="math_tutor",
    model=MODEL,
    # The description is what the coordinator reads when deciding where to route.
    description="Answers math questions with step-by-step working.",
    instruction="You are a math tutor. Solve the problem showing each step briefly.",
)

writing_tutor = LlmAgent(
    name="writing_tutor",
    model=MODEL,
    description="Helps with writing: grammar, style, and clarity.",
    instruction="You are a writing tutor. Improve the user's text and explain the key fixes.",
)

# Listing agents in sub_agents gives the coordinator a transfer_to_agent tool;
# routing is a model decision based on each specialist's description.
root_agent = LlmAgent(
    name="coordinator",
    model=MODEL,
    instruction=(
        "You are a tutoring receptionist. Route each request to the right specialist. "
        "Do not answer questions yourself. If no specialist fits, say what you can help with."
    ),
    sub_agents=[math_tutor, writing_tutor],
)
