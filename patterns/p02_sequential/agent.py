"""Pattern 02 — Sequential: agents run in a fixed order, each output feeding the next."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv()

MODEL = "gemini-2.5-flash"

triager = LlmAgent(
    name="triager",
    model=MODEL,
    instruction=(
        "Classify the customer's message as JSON with keys: "
        "category (billing/bug/how-to/other), urgency (low/medium/high), sentiment (calm/frustrated/angry). "
        "Output ONLY the JSON."
    ),
    output_key="triage",  # saves this agent's reply into session state under "triage"
)

drafter = LlmAgent(
    name="drafter",
    model=MODEL,
    instruction=(
        "Draft a reply to the customer's message. Match the approach to the triage: "
        "apologize first if they're frustrated or angry, escalate promises only if urgency is high.\n"
        "Output ONLY the draft reply.\n\n"
        "Triage:\n{triage}"  # {triage} is filled in from session state at runtime
    ),
    output_key="reply_draft",
)

tone_checker = LlmAgent(
    name="tone_checker",
    model=MODEL,
    instruction=(
        "Review this support reply: remove blame-y phrasing, corporate filler, and overpromises. "
        "Keep it warm and under 120 words. Output ONLY the final reply.\n\n"
        "Draft:\n{reply_draft}"
    ),
)

# Runs triager -> drafter -> tone_checker, always in this order — no model decides the flow.
root_agent = SequentialAgent(name="support_pipeline", sub_agents=[triager, drafter, tone_checker])
