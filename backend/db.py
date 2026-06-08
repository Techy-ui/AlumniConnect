import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="alumniconnect",
        user="postgres",
        password="Akash@1612",
        host="localhost",
        port="5432"
    )
