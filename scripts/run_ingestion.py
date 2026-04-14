from db.prices import get_latest_date
# from ingestion.alpha_fetcher import fetch_prices as avfp
from ingestion.financialmodeling_fetcher import fetch_symbols as fmfs
from db.prices import insert_prices
from db.symbols import ensure_symbol
from ingestion.fetcher import fetch, QuotaExceeded
from utils.logger import get_logger
import pandas as pd
import time
from enum import Enum

logger = get_logger()
# RATE_LIMIT_SECONDS = 12
# quota_exceeded = False

class symbol_scan(Enum):
    MOST_ACTIVES="most-actives"
    BIGGEST_LOSERS="biggest-losers"
    BIGGEST_GAINERS="biggest-gainers"

RATE_LIMITS = {
    "twelve": 8,
    "alpha": 15,
    "default_rate_limit": 12
}

def fetch_with_retry(symbol, provider, scan_type, run_id, retries=3, delay=5):

    for attempt in range(1, retries + 1):
        try:
            df = fetch(symbol, provider)
            return df, (attempt - 1)

        except QuotaExceeded:
            raise  # don't retry quota

        except Exception as e:
            logger.warning("retry_attempt", extra={
                "run_id": run_id,
                "event": "retry_attempt",
                "symbol": symbol,
                "provider": provider,
                "scan_type": scan_type.value,
                "attempt": attempt,
                "error": str(e)
            })

            if attempt == retries:
                raise

            time.sleep(delay * attempt)  # simple backoff

def main():
    run_id = int(time.time())
    start_time = time.time()
    provider = "twelve"
    logger.info("run_start", extra={
        "run_id": run_id,
        "event": "run_start",
        "provider": provider
    })
    seen = set()

    processed = 0
    success = 0
    failed = 0
    skipped = 0

    for scan_type in symbol_scan:
        #fetch symbols from provider
        symbols = fmfs(scan_type.value)

        if not isinstance(symbols, list):
            logger.error("invalid_symbols_response", extra={
                "run_id": run_id,
                "event": "invalid_symbols_response",
                "scan_type": scan_type.value
            })
            raise Exception("Invalid response from FMP")

        if not symbols:
            logger.warning("empty_symbol_list", extra={
                "run_id": run_id,
                "event": "empty_symbol_list",
                "scan_type": scan_type.value
            })
            continue

        logger.info("symbols_fetched", extra={
            "run_id": run_id,
            "event": "symbols_fetched",
            "provider": provider,
            "scan_type": scan_type.value,
            "count": len(symbols)
        })
        
        for ticker in symbols:
            symbol = ticker.get("symbol")

            if not symbol:
                logger.warning("missing_symbol", extra={
                    "run_id": run_id,
                    "event": "missing_symbol",
                    "scan_type": scan_type.value
                })
                continue

            if symbol in seen:
                continue

            seen.add(symbol)
            processed += 1

            name = ticker.get('name')
            exchange = ticker.get('exchange')

            df = None

            had_error = False
            try:
                df, retries = fetch_with_retry(symbol, provider, scan_type, run_id)
                logger.info("processing", extra={
                    "run_id": run_id,
                    "event": "processing",
                    "symbol": symbol,
                    "provider": provider,
                    "scan_type": scan_type.value,
                    "retries": retries if 'retries' in locals() else None
                })

            except QuotaExceeded:
                # provider persists across scans intentionally
                old_provider = provider
                logger.warning("provider_switch", extra={
                    "run_id": run_id,
                    "event": "provider_switch",
                    "reason": "quota_exceeded",
                    "scan_type": scan_type.value,
                    "from_provider": old_provider,
                    "to_provider": "alpha"
                })
                provider = "alpha"

                try:
                    df, retries = fetch_with_retry(symbol, provider, scan_type, run_id)
                    logger.info("processing", extra={
                        "run_id": run_id,
                        "event": "processing",
                        "symbol": symbol,
                        "provider": provider,
                        "scan_type": scan_type.value,
                        "retries": retries if 'retries' in locals() else None
                    })
                except Exception as e:
                    logger.error("alpha_fetch_failed", extra={
                        "run_id": run_id,
                        "event": "alpha_fetch_failed",
                        "symbol": symbol,
                        "provider": provider,
                        "scan_type": scan_type.value,
                        "error": str(e)
                    })
                    df = None
                    failed +=1
                    had_error = True

            except Exception as e:
                logger.error("fetch_failed", extra={
                    "run_id": run_id,
                    "event": "fetch_failed",
                    "symbol": symbol,
                    "provider": provider,
                    "scan_type": scan_type.value,
                    "error": str(e)
                })
                df = None
                failed +=1
                had_error = True
            
            # ✅ NOW ALWAYS runs if df exists
            if df is None or df.empty:
                logger.warning("no_data", extra={
                    "run_id": run_id,
                    "event": "no_data",
                    "symbol": symbol,
                    "provider": provider,
                    "scan_type": scan_type.value
                })
                if not had_error:
                    skipped += 1
            else:
                # 🔥 NEW: incremental filtering
                last_date = get_latest_date(symbol)

                if last_date:
                    last_date = pd.to_datetime(last_date) 
                    df["date"] = pd.to_datetime(df["date"])
                    df = df[df["date"] > last_date]

                # 🔥 NEW: handle no new rows
                if df.empty:
                    logger.info("no_new_data", extra={
                        "run_id": run_id,
                        "event": "no_new_data",
                        "symbol": symbol,
                        "provider": provider,
                        "scan_type": scan_type.value
                    })
                else:
                    ensure_symbol(symbol, name, exchange)
                    insert_prices(df)

                    logger.info("insert_success", extra={
                        "run_id": run_id,
                        "event": "insert_success",
                        "symbol": symbol,
                        "provider": provider,
                        "scan_type": scan_type.value,
                        "rows": len(df)
                    })
                    success += 1

            # # ✅ NOW ALWAYS runs if df exists
            # if df is None or df.empty:
            #     logger.warning("no_data", extra={
            #         "run_id": run_id,
            #         "event": "no_data",
            #         "symbol": symbol,
            #         "provider": provider,
            #         "scan_type": scan_type.value
            #     })
            #     if not had_error:
            #         skipped +=1
            # else:
            #     ensure_symbol(symbol, name, exchange)
            #     insert_prices(df)
            #     logger.info("insert_success", extra={
            #         "run_id": run_id,
            #         "event": "insert_success",
            #         "symbol": symbol,
            #         "provider": provider,
            #         "scan_type": scan_type.value,
            #         "rows": len(df)
            #     })
            #     success +=1

            # always
            time.sleep(RATE_LIMITS.get(provider, RATE_LIMITS["default_rate_limit"]))
        
    #SUMMARY
    logger.info("run_summary", extra={
        "run_id": run_id,
        "event": "run_summary",
        "duration_sec": round(time.time() - start_time, 2),
        "scan_types_processed": [s.value for s in symbol_scan],
        "unique_symbols": len(seen),
        "processed": processed,
        "final_provider": provider,
        "success": success,
        "failed": failed,
        "skipped": skipped
    })

        


if __name__ == "__main__":
    main()





# def run(symbol):
    # logger.info(f"\nProcessing {symbol}...")
    #get symbol latest date from prices table
    # last_date = get_latest_date(symbol)

    #fetch price from provider
    # df=tdfp(symbol)

    #df validation
    # if df is None or df.empty:
    #     logger.error(f"No data for {symbol}")
    #     return

    # if last_date:
    #     logger.info(f"Last date in DB for {symbol}: {last_date}")
    #     df["date"] = pd.to_datetime(df["date"]).dt.date
    #     df = df[df["date"] > last_date]
    #     logger.info(f"New rows for {symbol}: {len(df)}")

    # if df.empty:
    #     logger.warning(f"No new data for {symbol}")
    #     return

    #DB insert price
    # logger.info(f"{symbol} Fetched {len(df)} rows")
    # insert_prices(df)
    # logger.info(f"{symbol} Inserted successfully")

    # df = avfp(symbol)
    # ensure_symbol(symbol)
    # insert_prices(df)

            # try:
            #     df = fetch(symbol, provider)
            #     logger.info(f"[{provider}] Processing {symbol}")
            
            # except QuotaExceeded:
            #     logger.error("TwelveData quota exceeded — switching to Alpha")
            #     provider = "alpha"

            #     try:
            #         df = fetch(symbol, provider)
            #         logger.info(f"{provider}] Processing {symbol}")
                    
            #     except Exception as e:
            #         logger.error(f"Alpha failed for {symbol}: {e}")
            #         break

            # except Exception as e:
            #     logger.error(f"{symbol}: {e}")
            #     continue

            # else:
            #     if df is None or df.empty:
            #         logger.warning(f"No data for {symbol}")

            #     else:
            #         ensure_symbol(symbol, name, exchange)
            #         insert_prices(df)
                
            # finally:
            #     time.sleep(RATE_LIMIT_SECONDS) 

#############################################################################################################
                # symbol = ticker.get("symbol")

                # logger(f"[INFO] Processing {symbol}")

                # try:
                #     if provider == "twelve":
                #         df = fetch(symbol)
                #     else:
                #         df = avfp(symbol)

                # except QuotaExceeded:
                #     logger("[ERROR] TwelveData quota exceeded — switching to Alpha")

                #     provider = "alpha"

                #     try:
                #         df = avfp(symbol)
                #     except Exception as e:
                #         logger(f"[ERROR] Alpha failed for {symbol}: {e}")
                #         break

                # except Exception as e:
                #     logger(f"[ERROR] {symbol}: {e}")
                #     continue

                # if df is None or df.empty:
                #     logger(f"[WARN] No data for {symbol}")
                #     continue

                # # 👉 your existing pipeline continues
                # ensure_symbol(symbol, ...)
                # insert_prices(df)

            # if quota_exceeded:
            #     logger("Stopping ingestion — quota exceeded")
            #     break

            # try:
            #     symbol = ticker.get('symbol')

            #     if symbol in seen:
            #         continue
            #     seen.add(symbol)
                

            #     name = ticker.get('name')
            #     exchange = ticker.get('exchange')

                # price = ticker.get('price')
                # change = ticker.get('change')
                # changesPercentage = ticker.get('changesPercentage')
                

                #DB insert symbol
            #     ensure_symbol(symbol, name, exchange)
            #     run(symbol)
            #     time.sleep(RATE_LIMIT_SECONDS) 

            # except Exception as e:
            #     logger(f"Error processing {symbol}: {e}")




    # symbols = ["AAPL", "MSFT", "TSLA"]
    # for s in symbols:
    #     tdfp(s)


    # for symbol in symbols:
    #     try:
    #         run(symbol)
    #         time.sleep(12)  # REQUIRED (rate limit)
    #     except Exception as e:
    #         logger(f"Error: {e}")

