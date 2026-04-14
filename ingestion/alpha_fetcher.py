import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def fetch_prices(symbol: str):
    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise Exception(f"API error: {data}")

    ts = data["Time Series (Daily)"]

    rows = []

    for date, values in ts.items():
        rows.append({
            "symbol": symbol,
            "date": date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        })

    df = pd.DataFrame(rows)

    return df