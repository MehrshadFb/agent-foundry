"""Pattern 04 — Loop & Critique: generator + critic loop until the critic approves or max iterations."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import exit_loop

load_dotenv()

MODEL = "gemini-2.5-flash"

generator = LlmAgent(
    name="generator",
    model=MODEL,
    instruction=(
        "Write ONE tagline for the product the user describes. Output ONLY the tagline.\n"
        "If there is critic feedback below, write an improved version that addresses it.\n\n"
        "Critic feedback (empty on the first pass):\n{feedback?}"  # ? = optional, may not exist yet
    ),
    output_key="tagline",
)

critic = LlmAgent(
    name="critic",
    model=MODEL,
    instruction=(
        "You are a strict critic. Evaluate this tagline:\n{tagline}\n\n"
        "Criteria: under 8 words, memorable, no clichés like 'revolutionary' or 'next-level'.\n"
        "If it meets ALL criteria, call the exit_loop tool.\n"
        "Otherwise output ONLY one specific improvement to make — no praise, no preamble."
    ),
    tools=[exit_loop],  # calling this tool stops the loop early
    output_key="feedback",
)

# Repeats generator -> critic until exit_loop is called or 3 rounds pass.
root_agent = LoopAgent(
    name="refine_until_good",
    sub_agents=[generator, critic],
    max_iterations=3,
)
