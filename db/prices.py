from db.connection import get_connection
from psycopg2.extras import execute_values

def get_latest_date(symbol):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(date) AS latest_date
        FROM prod.prices
        WHERE symbol = %s
    """, (symbol,))

    row = cur.fetchone()

    cur.close()
    conn.close()


    if row is None or row["latest_date"] is None:
        return None

    return row['latest_date']


def insert_prices(df):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO prod.prices (symbol, date, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (symbol, date) DO NOTHING
    """

    values = [
        (
            row.symbol,
            row.date,
            row.open,
            row.high,
            row.low,
            row.close,
            int(row.volume)
        )
        for row in df.itertuples(index=False)
    ]

    execute_values(cur, query, values)

    conn.commit()
    cur.close()
    conn.close()