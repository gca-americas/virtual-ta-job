import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    from database import get_db_connection
except ImportError:
    # Fallback inherently resolving local root development contexts statically
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from database import get_db_connection


def generate_daily_test_events():
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # 1. Select the top 10 courses natively that need testing structurally
        cur.execute("""
            SELECT id, name FROM courses 
            WHERE is_published = TRUE
            ORDER BY last_eval_date ASC NULLS FIRST 
            LIMIT 10
        """)
        courses = cur.fetchall()

        if not courses:
            print("No actionable courses found mathematically skipping payload.")
            return

        today = date.today()
        tomorrow = today + timedelta(days=1)

        base_date = today.strftime("%y%m%d")

        for idx, course in enumerate(courses):
            event_id = f"eval-{base_date}-{idx + 1}"
            event_name = (
                f"Daily Test Framework - {course[1]} ({today.strftime('%Y-%m-%d')})"
            )

            print(
                f"Orchestrating test bounds for Event: {event_id} (Course: {course[0]})"
            )

            # 2. Map row definitions directly into `events` simulating user input dynamically
            cur.execute(
                """
                INSERT INTO events (id, event_name, start_date, end_date, language, country, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (
                    event_id,
                    event_name,
                    today,
                    tomorrow,
                    "en",
                    "US",
                    "eval_agent_service",
                ),
            )

            # 3. Synchronize this specific course natively mapping it 1:1 against the test event
            cur.execute(
                """
                INSERT INTO event_courses (event_id, course_id)
                VALUES (%s, %s)
                ON CONFLICT (event_id, course_id) DO NOTHING
            """,
                (event_id, course[0]),
            )

        conn.commit()
        print(
            f"Successfully staged {len(courses)} courses against {event_id} structurally anticipating Hourly build-loop!"
        )

    except Exception as e:
        conn.rollback()
        print(f"Failed to cleanly provision daily evaluations natively: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    generate_daily_test_events()
