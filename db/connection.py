import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="quantengine",
        user="qe_user",
        password="StrongPassword123",
        port=5432,
        cursor_factory=RealDictCursor
    )