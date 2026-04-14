from db.connection import get_connection

def ensure_symbol(symbol, name, exchange):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prod.symbols (symbol, name, exchange)
        VALUES (%s, %s, %s)
        ON CONFLICT (symbol) DO NOTHING
    """, (symbol, name, exchange))

    conn.commit()
    cur.close()
    conn.close()

