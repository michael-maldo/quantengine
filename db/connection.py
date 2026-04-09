import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


def get_env(var):
    value = os.getenv(var)
    if not value:
        raise Exception(f"Missing environment variable: {var}")
    return value

def get_connection():
    return psycopg2.connect(
        host=get_env("DB_HOST"),
        database=get_env("DB_NAME"),
        user=get_env("DB_USER"),
        password=get_env("DB_PASSWORD"),
        port=get_env("DB_PORT"),
        cursor_factory=RealDictCursor
    )
