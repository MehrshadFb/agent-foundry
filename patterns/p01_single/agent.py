"""Pattern 01 — Single: one agent with multiple tools handles the whole task."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()

MODEL = "gemini-2.5-flash"


def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b


root_agent = LlmAgent(
    name="calculator",
    model=MODEL,
    instruction="You are a calculator assistant. Always use the tools to compute, never do math in your head.",
    tools=[add, multiply],
)
