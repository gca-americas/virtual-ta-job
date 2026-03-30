from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

model = Gemini(
    model="gemini-2.5-pro",
    retry_options=types.HttpRetryOptions(
        attempts=3, exp_base=5, initial_delay=1, http_status_codes=[429, 500, 503, 504]
    ),
)

question_agent = Agent(
    name="QuestionGenerator",
    model=model,
    instruction="""
    You are an AI generating an evaluation dataset for a Virtual Teaching Assistant.
    Generate EXACTLY 65 questions mapped to these personas:
    - 20 'beginner': No GCP knowledge, no prior coding experience, dumb questions.
    - 20 'careless': Skipped steps, forgot to put things wrong place, bad copy-paste, didn't read.
    - 10 'faq': User frequently asked common errors.
    - 15 'advanced': Conceptual deep architectural questions.

    CRITICAL FORMATTING INSTRUCTION: 
    When generating these questions, DO NOT just ask plain text questions. You must simulate real developer environments. 
    About 40% of the questions must mechanically mimic the exact payload format sent by our VS Code IDE Extension, which looks like this:
    
    [Source: IDE]
    File: main.py
    ## Code Snapshot
    ```python
    <insert broken or snippet code here>
    ```
    ## Active Diagnostics (Errors/Warnings)
    <insert mock lint errors or syntax tracebacks here, or 'None'>
    ## User Query
    <insert the user's actual question here>
    
    For the other 60%, frequently include raw mock terminal tracebacks, messy JSON dumps, or broken code snippets pasted directly into the text, just like a frustrated user would do.

    Each item must contain "level", "question", and "prefer_answer" string fields strictly mapping the expected Virtual TA helpful response based on the course materials!
    Return a pure JSON list format. Do not use markdown wrappers.
    """
)
