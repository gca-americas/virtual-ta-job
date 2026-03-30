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
    Generate EXACTLY 50 questions mapped to these personas:
    - 15 'beginner': Users with no prior Google Cloud experience. They lack context on fundamental cloud concepts, require step-by-step guidance, and often misunderstand foundational technical terms.
    - 18 'careless': Users who rapidly skim instructions. They frequently skip mandatory setup steps, execute commands in the wrong directory, incorrectly copy-paste file contents, or ignore prerequisite warnings.
    - 7 'faq': Users encountering the most statistically common blockers tailored to the specific course material (e.g., IAM permission errors, missing API enablement, syntax typos).
    - 10 'advanced': Experienced developers asking conceptual, architectural, or "why" questions to deeply understand the framework design rather than just blindly following instructions.

    CRITICAL FORMATTING INSTRUCTION: 
    When generating these questions, DO NOT just ask plain text questions. You must strictly simulate real developer environments and how the Workshop-TA plugin actually formulates its telemetry inputs. 
    
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
    
    For 30%, mathematically mimic the terminal extension integration which captures raw stack traces automatically:
    
    [Source: Terminal]
    ## Terminal Output
    <insert raw crash dump, trace, or gcloud failure payload here>
    ## User Query
    <insert terminal-related question here>

    For 15%, simulate users manually pasting messy JSON dumps, broken code blocks, or raw error outputs directly into the unstructured text chat window without any formatting brackets.
    For 10%, simulate users typing entirely normal, plain-text questions naturally without pasting any code or tracebacks at all.
    For the remaining 5%, simulate unpredictable malicious behavior, such as prompt injection attacks, jailbreak attempts, or completely irrelevant random gibberish.

    Each item must contain "level", "question", and "prefer_answer" string fields strictly mapping the expected Virtual TA helpful response based on the course materials!
    Return a pure JSON list format. Do not use markdown wrappers.
    """,
)
