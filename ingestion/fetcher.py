from ingestion.twelvedata_fetcher import fetch_raw, parse_prices, is_quota_exceeded
from ingestion.alpha_fetcher import fetch_prices as avfp
from utils.logger import get_logger

logger = get_logger()

def fetch_with_fallback(symbol):
    data = fetch_raw(symbol)

    if is_quota_exceeded(data):
        print("TwelveData quota exceeded — switching to Alpha")
        return avfp(symbol)

    if "values" not in data:
        print(f"Skipping {symbol}: {data.get('message')}")
        return None

    return parse_prices(symbol, data)

class QuotaExceeded(Exception):
    pass

def fetch(symbol, provider):
    logger.info("processing", extra={
        "event": "processing",
        "symbol": symbol,
        "provider": provider
    })
    
    if provider == "twelve":
        data = fetch_raw(symbol)

        if is_quota_exceeded(data):
            print("TwelveData quota exceeded — switching to Alpha")
            raise QuotaExceeded("TwelveData quota exceeded")
    
        if "values" not in data:
            print(f"[WARN] Skipping {symbol}: {data.get('message')}")
            return None

        return parse_prices(symbol, data)

    elif provider == "alpha":
        return avfp(symbol)

    else:
        raise ValueError(f"Unknown provider: {provider}")

def fetch_old(symbol):
    data = fetch_raw(symbol)

    if is_quota_exceeded(data):
        print("TwelveData quota exceeded — switching to Alpha")
        raise QuotaExceeded("TwelveData quota exceeded")
        # return avfp(symbol)


    # Invalid symbol / bad data
    if "values" not in data:
        print(f"[WARN] Skipping {symbol}: {data.get('message')}")
        return None

    # Normal path
    return parse_prices(symbol, data)