import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="alumniconnect",
        user="postgres",
        password="Akash@1612",
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )