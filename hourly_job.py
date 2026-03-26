import os
import json
from datetime import date
from database import get_db_connection
from google.cloud import pubsub_v1

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
publisher = pubsub_v1.PublisherClient()
deploy_topic_path = publisher.topic_path(project_id, "deploy_queue")
demolish_topic_path = publisher.topic_path(project_id, "demolish_queue")


def run_hourly_check():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        today = date.today()

        # 1. Start scheduled deployments
        cur.execute(
            """
            SELECT e.id, e.event_name, e.start_date, e.end_date
            FROM events e
            LEFT JOIN running_logs r ON e.id = r.event_id
            WHERE e.start_date <= %s AND e.end_date >= %s AND r.event_id IS NULL
        """,
            (today, today),
        )

        columns = [desc[0] for desc in cur.description]
        to_deploy = [dict(zip(columns, row)) for row in cur.fetchall()]

        for event in to_deploy:
            cur.execute(
                """
                SELECT c.id, c.repo_url, c.directory_root 
                FROM event_courses ec
                JOIN courses c ON ec.course_id = c.id
                WHERE ec.event_id = %s
            """,
                (event["id"],),
            )

            repo_map = {}
            for r in cur.fetchall():
                c_id, url, root = r[0], r[1], r[2]
                if root.startswith("/"):
                    root = root[1:]
                if root and not root.endswith("/"):
                    root += "/"

                path = f"{root}{c_id}"
                if url not in repo_map:
                    repo_map[url] = {"url": url, "paths": []}
                repo_map[url]["paths"].append(path)

            repos_payload = list(repo_map.values())

            service_name = f"workshop-{event['id']}"

            cur.execute(
                """
                INSERT INTO running_logs 
                (event_id, event_name, cloud_run_service_name, scheduled_start_date, scheduled_end_date, repos_to_read, folders_to_load, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'DEPLOYING')
            """,
                (
                    event["id"],
                    event["event_name"],
                    service_name,
                    event["start_date"],
                    event["end_date"],
                    json.dumps([r["url"] for r in repos_payload]),
                    json.dumps(repos_payload),
                ),
            )

            payload = {
                "event_id": event["id"],
                "event_name": event["event_name"],
                "service_name": service_name,
                "repos": repos_payload,
            }
            future = publisher.publish(deploy_topic_path, json.dumps(payload).encode("utf-8"))
            future.result()
            print(f"Issued deploy orchestrator sequence for {event['id']}")

        # 2. Rip down expired environments
        cur.execute(
            """
            SELECT event_id, cloud_run_service_name 
            FROM running_logs 
            WHERE scheduled_end_date < %s AND status != 'DEMOLISHED' AND status != 'DEMOLISHING'
        """,
            (today,),
        )

        to_demolish = cur.fetchall()
        for row in to_demolish:
            event_id, service_name = row[0], row[1]
            payload = {"event_id": event_id, "service_name": service_name}
            future = publisher.publish(demolish_topic_path, json.dumps(payload).encode("utf-8"))
            future.result()

            cur.execute(
                "UPDATE running_logs SET status = 'DEMOLISHING' WHERE event_id = %s",
                (event_id,),
            )
            print(f"Issued demolish orchestrator sequence for {event_id}")

        conn.commit()
    except Exception as e:
        print(f"Hourly processing failed natively: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    run_hourly_check()
