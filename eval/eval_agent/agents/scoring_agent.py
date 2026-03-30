from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

model = Gemini(
    model="gemini-2.5-pro",
    retry_options=types.HttpRetryOptions(
        attempts=3, exp_base=5, initial_delay=1, http_status_codes=[429, 500, 503, 504]
    ),
)

scoring_agent = Agent(
    name="ScoreEvaluator",
    model=model,
    instruction="""
    You are an Expert Grader grading a Virtual Teaching Assistant LLM.
    You will be given a list of questions, the "prefer_answer" dictating what it should have said, and the actual "ta_answer" retrieved.
    Compare ta_answer against prefer_answer across the set.
    Generate a pure JSON output containing 'score' (percentage) and 'suggest_update' (markdown text to fix halluctions).
    """
)
