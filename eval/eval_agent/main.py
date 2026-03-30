import os
import sys
import json
import time
import requests
import datetime
import tempfile
import shutil
from git import Repo
from dotenv import load_dotenv
from google.genai import types
import asyncio

# ADK Runner module abstracted explicitly per architecture rules
from runner import get_question_runner, get_scoring_runner

try:
    from database import get_db_connection
except ImportError:
    # Append repo root to load centralized DB module locally bypassing the Docker layer!
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from database import get_db_connection


load_dotenv()


def clone_repo_and_read(repo_url, filter_path=""):
    ext_stripped = repo_url
    if repo_url.endswith(".git"):
        ext_stripped = repo_url[:-4]

    tmp_dir = tempfile.mkdtemp(prefix="eval_repo_")
    print(f"Cloning {ext_stripped} to {tmp_dir}...")
    try:
        Repo.clone_from(ext_stripped, tmp_dir)
    except Exception as e:
        print(f"Git clone failed: {e}")
        return ""

    target_dir = os.path.join(tmp_dir, filter_path) if filter_path else tmp_dir
    if not os.path.exists(target_dir):
        target_dir = tmp_dir
        
    combined_docs = ""
    for root, dirs, files in os.walk(target_dir):
        if ".git" in root:
            continue
        for f in files:
            file_path = os.path.join(root, f)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    rel_path = os.path.relpath(file_path, tmp_dir)
                    combined_docs += f"\n--- {rel_path} ---\n{content}\n"
            except Exception:
                pass
    shutil.rmtree(tmp_dir)
    return combined_docs


def extract_adk_text(event) -> str:
    text = ""
    if hasattr(event, "model_turn") and event.model_turn:
        for part in event.model_turn.parts:
            if hasattr(part, "text") and part.text:
                text += part.text
    elif hasattr(event, "text") and event.text:
        text += event.text
    elif hasattr(event, "content") and event.content:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text
    return text


def run_eval():
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # Actively poll running_logs natively seeking deployed test servers that haven't been evaluated yet
        cur.execute(
            """
            SELECT rl.event_id, rl.cloud_run_url 
            FROM running_logs rl
            JOIN events e ON rl.event_id = e.id
            WHERE rl.status = 'RUNNING' AND e.created_by = 'eval_agent_service'
        """
        )
        queued_events = cur.fetchall()

        if not queued_events:
            print("No actionable synthetic testing infrastructures currently RUNNING. Exiting cleanly.")
            return

        for event_row in queued_events:
            event_id, cloud_run_url = event_row[0], event_row[1]

            # Lock the execution loop natively protecting from duplicate cron hooks
            cur.execute("UPDATE running_logs SET status = 'EVALUATING' WHERE event_id = %s", (event_id,))
            conn.commit()

            run_url = cloud_run_url.rstrip("/")
            
            cur.execute(
                """
                SELECT c.id, c.repo_url, c.directory_root FROM courses c
                JOIN event_courses ec ON c.id = ec.course_id
                WHERE ec.event_id = %s
                """, (event_id,)
            )
            courses = cur.fetchall()

            for course in courses:
                course_id, repo_url, root_dir = course[0], course[1], course[2]
                
                # Mirror hourly_job path resolution logically mapping exact nested boundaries natively
                r_dir = root_dir if root_dir else ""
                if r_dir.startswith("/"):
                    r_dir = r_dir[1:]
                if r_dir and not r_dir.endswith("/"):
                    r_dir += "/"
                target_path = f"{r_dir}{course_id}"

                print(f"Beginning ADK Eval pipeline for event: {event_id} course: {course_id} on {run_url}")

                eval_dt = datetime.datetime.now()
                context_string = clone_repo_and_read(repo_url, target_path)

            # ADK RUN 1: Generator
            print("1. Running Generator Agent...")
            gen_runner = get_question_runner()
            try:
                # Synchronously initialize the mandatory ADK session block natively satisfying structural dependencies
                asyncio.run(gen_runner.session_service.create_session(
                    app_name="EvalQuestionAgent", 
                    user_id="eval_user", 
                    session_id=f"eval_session_{course_id}"
                ))
                
                # Fire async/sync ADK run structurally passing Context as Prompt organically wrapped
                agent_res = gen_runner.run(
                    user_id="eval_user",
                    session_id=f"eval_session_{course_id}",
                    new_message=types.Content(role="user", parts=[types.Part.from_text(text=f"Context Docs: {context_string[:80000]}")])
                )
                
                # ADK physically returns a streaming generator; seamlessly unpack and join it organically!
                assembled_json, last_t = "", ""
                if hasattr(agent_res, "__iter__") and not isinstance(agent_res, (str, list, dict)):
                    for event in agent_res:
                        evt_text = extract_adk_text(event)
                        if evt_text and evt_text != last_t:
                            if evt_text.startswith(last_t):
                                assembled_json += evt_text[len(last_t):]
                            else:
                                assembled_json += evt_text
                            last_t = evt_text
                else:
                    assembled_json = extract_adk_text(agent_res)
                
                # Strip markdown logic defensively returning parsed JSON locally
                raw_json = assembled_json.strip("```json").strip("```").strip()
                questions_payload = json.loads(raw_json)

                # Natively purge the ADK memory boundary efficiently releasing short-term RAM storage seamlessly
                asyncio.run(gen_runner.session_service.delete_session(
                    app_name="EvalQuestionAgent", 
                    user_id="eval_user", 
                    session_id=f"eval_session_{course_id}"
                ))

            except Exception as e:
                print(f"Agent Prompt Failed structurally parsing JSON stream: {e}")
                continue

            full_logs = []
            print(f"2. Simulating {len(questions_payload)} API Calls...")
            for idx, q_item in enumerate(questions_payload):
                level = q_item.get("level")
                question_text = q_item.get("question")
                prefer_answer = q_item.get("prefer_answer")

                print(f"  -> [{(idx+1)}/{len(questions_payload)}] Testing [{level}]: {question_text[:60]}...")
                ta_ans = "TIMEOUT"
                try:
                    resp = requests.post(
                        f"{run_url}/api/chat",
                        data={
                            "name": f"Eval_{level}",
                            "workshop": course_id,
                            "message": question_text,
                            "interface": "web",
                        },
                        timeout=120,
                    )
                    ta_ans = resp.text if resp.status_code == 200 else str(resp.content)
                    print(f"     TA replied ({resp.status_code}): {ta_ans[:80]}...")
                except Exception as e:
                    print(f"     Error querying TA: {e}")

                cur.execute(
                    """
                    INSERT INTO eval_log (event_id, course_id, eval_date_time, level, question_number, question, prefer_answer, ta_answer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        event_id,
                        course_id,
                        eval_dt,
                        level,
                        idx,
                        question_text,
                        prefer_answer,
                        ta_ans,
                    ),
                )
                conn.commit()

                full_logs.append(
                    {
                        "question": question_text,
                        "prefer_answer": prefer_answer,
                        "ta_answer": ta_ans,
                    }
                )
                time.sleep(2)

            # ADK RUN 2: Scoring Agent
            print("3. Running Scoring Agent...")
            score_runner = get_scoring_runner()
            try:
                # Synchronously initialize the mandatory ADK session block natively satisfying structural dependencies
                asyncio.run(score_runner.session_service.create_session(
                    app_name="EvalScoringAgent", 
                    user_id="eval_scorer", 
                    session_id=f"score_session_{course_id}"
                ))
                
                score_res = score_runner.run(
                    user_id="eval_scorer",
                    session_id=f"score_session_{course_id}",
                    new_message=types.Content(role="user", parts=[types.Part.from_text(text=f"Context Docs: {context_string[:80000]}\n\nPayload logs: {json.dumps(full_logs)}")])
                )
                
                # ADK physically returns a streaming generator; seamlessly unpack and join it organically!
                assembled_score, last_s = "", ""
                if hasattr(score_res, "__iter__") and not isinstance(score_res, (str, list, dict)):
                    for event in score_res:
                        ext_text = extract_adk_text(event)
                        if ext_text and ext_text != last_s:
                            if ext_text.startswith(last_s):
                                assembled_score += ext_text[len(last_s):]
                            else:
                                assembled_score += ext_text
                            last_s = ext_text
                else:
                    assembled_score = extract_adk_text(score_res)
                
                raw_score = assembled_score.strip("```json").strip("```").strip()
                print(f"  -> Raw Evaluator Payload: {raw_score[:120]}...")
                grade = json.loads(raw_score)
                final_score = grade.get("score", "0%")
                suggest_update = grade.get("suggest_update", "")

                # Aggressively detach the scoring session dynamically terminating the conversational history loop
                asyncio.run(score_runner.session_service.delete_session(
                    app_name="EvalScoringAgent", 
                    user_id="eval_scorer", 
                    session_id=f"score_session_{course_id}"
                ))

            except Exception as e:
                print(f"  -> ERROR: Agent Parsing Failed: {e}")
                final_score, suggest_update = "0%", f"Agent Parsing Error: {e}"

            cur.execute(
                """
                INSERT INTO eval_suggestion (course_id, eval_date_time, score, suggest_update)
                VALUES (%s, %s, %s, %s)
            """,
                (course_id, eval_dt, final_score, suggest_update),
            )

            cur.execute(
                """
                UPDATE courses SET last_eval_date = %s, eval_score = %s, last_update_date = CURRENT_TIMESTAMP
                WHERE id = %s
            """,
                (eval_dt, final_score, course_id),
            )
            conn.commit()
            print(f"Course Completed! Score: {final_score}")

        # Cleanly lift the EVALUATING lock and flag the infrastructure entirely EVALUATED logically marking it for Demolition!
        cur.execute("UPDATE running_logs SET status = 'EVALUATED' WHERE event_id = %s", (event_id,))
        conn.commit()
        print(f"Test Event {event_id} structurally finalized all course pipelines efficiently terminating script loop!")

    except Exception as e:
        print(f"Eval Loop Fatal: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run_eval()
