# from db.connection import get_connection

# def get_latest_date(symbol):
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT MAX(date) AS latest_date
#         FROM prod.price
#         WHERE symbol = %s
#     """, (symbol,))

#     row = cur.fetchone()

#     cur.close()
#     conn.close()


#     if row is None or row["latest_date"] is None:
#         return None

#     return row['latest_date']    