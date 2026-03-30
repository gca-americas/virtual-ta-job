from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents.question_agent import question_agent
from agents.scoring_agent import scoring_agent


def get_question_runner():
    session_service = InMemorySessionService()
    return Runner(
        app_name="EvalQuestionAgent",
        agent=question_agent,
        session_service=session_service,
    )


def get_scoring_runner():
    session_service = InMemorySessionService()
    return Runner(
        app_name="EvalScoringAgent",
        agent=scoring_agent,
        session_service=session_service,
    )
