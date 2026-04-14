import os
import requests
from dotenv import load_dotenv
import pandas as pd


load_dotenv()
key = os.getenv("TWELVE_DATA_API_KEY")

def fetch_raw(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={key}"

    response = requests.get(url, timeout=10)
    data = response.json()

    print(url)

    return data

def is_quota_exceeded(data):
    return (
        isinstance(data, dict)
        and data.get("status") == "error"
        and data.get("code") == 429
    )

def parse_prices(symbol, data):
    ts = data["values"]

    rows = []

    for intraday in ts:
        rows.append({
            "symbol": symbol,
            "date": intraday.get("datetime"),
            "open": float(intraday.get("open")),
            "high": float(intraday.get("high")),
            "low": float(intraday.get("low")),
            "close": float(intraday.get("close")),
            "volume": int(intraday.get("volume")),
        })

    return pd.DataFrame(rows)

# def fetch_prices(symbol):
#     # print(f"{symbol}")
#     # url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={key}"

#     # response = requests.get(url)
#     data = fetch_raw(symbol)

#     # HANDLE ERRORS HERE
#     if is_quota_exceeded(data):
#         raise Exception("QUOTA_EXCEEDED")

#     if "values" not in data:
#         print(f"Skipping {symbol}: {data.get('message')}")
#         return None

#     ts = data["values"]

#     rows = []

#     for intraday in ts:
#         datetime = intraday.get("datetime")
#         open = float(intraday.get("open"))
#         high = float(intraday.get("high"))
#         low = float(intraday.get("low"))
#         close = float(intraday.get("close"))
#         volume = int(intraday.get("volume"))

#         rows.append({
#             "symbol": symbol,
#             "date": datetime,
#             "open": open,
#             "high": high,
#             "low": low,
#             "close": close,
#             "volume": volume,
#         })

#     df = pd.DataFrame(rows)

#     return df
