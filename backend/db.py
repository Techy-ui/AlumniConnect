import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():

    database_url = os.getenv("DATABASE_URL")

    # Production (Render)
    if database_url:
        return psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )

    # Local development
    return psycopg2.connect(
        dbname="alumniconnect",
        user="postgres",
        password=os.getenv("DB_PASSWORD", ""),
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )