"""Pattern 03 — Parallel: sub-agents fan out simultaneously, a synthesizer merges results."""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv()

MODEL = "gemini-2.5-flash"

optimist = LlmAgent(
    name="optimist",
    model=MODEL,
    instruction=(
        "List the 3 strongest arguments FOR the user's idea. "
        "Output ONLY the numbered arguments, one line each."
    ),
    output_key="pros",
)

skeptic = LlmAgent(
    name="skeptic",
    model=MODEL,
    instruction=(
        "List the 3 strongest arguments AGAINST the user's idea. "
        "Output ONLY the numbered arguments, one line each."
    ),
    output_key="cons",
)

synthesizer = LlmAgent(
    name="synthesizer",
    model=MODEL,
    instruction=(
        "Weigh both sides and give a balanced verdict with a clear recommendation. "
        "Output ONLY the verdict paragraph.\n\n"
        "Arguments for:\n{pros}\n\nArguments against:\n{cons}"
    ),
)

# The fan-out: optimist and skeptic run at the same time, in isolation —
# neither sees the other's output. Both land in session state.
fan_out = ParallelAgent(name="fan_out", sub_agents=[optimist, skeptic])

# The gather: parallel branches can't produce one answer, so the fan-out is
# wrapped in a SequentialAgent with a synthesizer that reads both results.
root_agent = SequentialAgent(name="debate", sub_agents=[fan_out, synthesizer])
