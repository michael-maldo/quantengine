from db.connection import get_connection

conn = get_connection()
cur = conn.cursor()

# Check table exists
cur.execute("""
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'pricesX'
);
""")

result = cur.fetchone()

if not result['exists']:
    raise Exception("prices table does not exist")

print("Schema OK")

cur.close()
conn.close()