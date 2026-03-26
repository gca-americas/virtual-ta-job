import os
import pg8000
from google.cloud.sql.connector import Connector, IPTypes

def get_db_connection():
    connector = Connector()
    def getconn() -> pg8000.dbapi.Connection:
        conn = connector.connect(
            os.environ.get("CLOUD_SQL_CONNECTION_NAME", ""),
            "pg8000",
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASS", ""),
            db=os.environ.get("DB_NAME", "postgres"),
            ip_type=IPTypes.PUBLIC
        )
        return conn

    return getconn()
