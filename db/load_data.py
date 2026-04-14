# # print("ETL pipeline starting...")

# from psycopg2.extras import execute_values
# from db.connection import get_connection
# # from ingestion.alpha_fetcher import fetchprices

# def ensure_symbol(symbol, name, exchange):
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         INSERT INTO prod.symbols (symbol, name, exchange)
#         VALUES (%s, %s, %s)
#         ON CONFLICT (symbol) DO NOTHING
#     """, (symbol, name, exchange))

#     conn.commit()
#     cur.close()
#     conn.close()


# def insert_prices(df):
#     conn = get_connection()
#     cur = conn.cursor()

#     query = """
#         INSERT INTO prod.price (symbol, date, open, high, low, close, volume)
#         VALUES %s
#         ON CONFLICT (symbol, date) DO NOTHING
#     """

#     values = [
#         (
#             row.symbol,
#             row.date,
#             row.open,
#             row.high,
#             row.low,
#             row.close,
#             int(row.volume)
#         )
#         for row in df.itertuples(index=False)
#     ]

#     execute_values(cur, query, values)

#     conn.commit()
#     cur.close()
#     conn.close()
