import os
import pg8000
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import secretmanager

# Optional fallback: load from Secret Manager natively if not already passed via Cloud Build availableSecrets
if not os.environ.get("DB_PASS"):
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        client = secretmanager.SecretManagerServiceClient()
        secret_name = (
            f"projects/{project_id}/secrets/events-db-credentials/versions/latest"
        )
        response = client.access_secret_version(request={"name": secret_name})
        secret_payload = response.payload.data.decode("utf-8")

        for line in secret_payload.strip().split("\n"):
            if line.startswith("export "):
                line = line[7:].strip()
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip(" '\"")
                    os.environ[key] = val
        print("Loaded DB credentials from Secret Manager natively.")
    except Exception as e:
        print(f"Secret Manager auto-load skipped or failed: {e}")


def get_db_connection():
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn = connector.connect(
            os.environ.get("CLOUD_SQL_CONNECTION_NAME", ""),
            "pg8000",
            user=os.environ.get("DB_USER", "admin"),
            password=os.environ.get("DB_PASS", ""),
            db=os.environ.get("DB_NAME", "events_db"),
            ip_type=IPTypes.PUBLIC,
        )
        return conn

    return getconn()
