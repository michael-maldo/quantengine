from db.connection import get_connection


def check_tables_exist():
    conn = get_connection()
    cur = conn.cursor()

    tables = ["symbols", "prices", "features", "fundamentals"]

    query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name = %s
    ) AS exists;
    """

    missing_tables = []

    try:
        for table in tables:
            cur.execute(query, ("prod", table))
            result = cur.fetchone()

            exists = result["exists"]

            if not exists:
                missing_tables.append(table)

        if missing_tables:
            raise Exception(f"Missing tables in schema 'prod': {', '.join(missing_tables)}")

        print("✅ Schema OK — all tables exist in 'prod'")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    check_tables_exist()