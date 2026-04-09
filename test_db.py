from db.connection import get_connection

conn = get_connection()
cur = conn.cursor()

# Check table exists
tables = ["symbols", "price", "features", "fundamentals"]

for table in tables:
    cur.execute(f"""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'prod'
        AND table_name = '{table}'
    );
    """)

    result = cur.fetchone()

    if not result['exists']:
        raise Exception(f"{table} table does not exist")

print("Schema OK")

cur.close()
conn.close()