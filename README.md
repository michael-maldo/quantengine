# QuantEngine – Stock Data Ingestion Pipeline

A production-style stock data ingestion pipeline that fetches, processes, and stores market data from multiple providers with fault tolerance and structured logging.

---

## Overview

QuantEngine is designed to simulate a real-world data engineering pipeline:

- Discovers active market symbols
- Fetches historical price data from multiple APIs
- Handles API limits and failures gracefully
- Stores data incrementally in PostgreSQL
- Provides structured JSON logs for observability

---

## Goal
To demonstrate backend, data engineering, and DevOps skills through a production-style system.


## Features
- Data ingestion pipeline (Python)
- PostgreSQL storage
- Feature engineering
- Backtesting engine
- Spring Boot API
- CI/CD with GitLab
- Monitoring with Prometheus


## Key Features

### Multi-Provider Data Ingestion
- TwelveData (primary)
- Alpha Vantage (fallback)
- Automatic provider switching on quota exhaustion

---

### Symbol Discovery
- Fetches symbols from:
  - Most Active
  - Biggest Gainers
  - Biggest Losers
- Stores symbols in database (deduplicated)

---

### Incremental Loading
- Only inserts **new price data**
- Uses latest stored date per symbol
- Avoids duplicate ingestion

---

### Retry + Fault Tolerance
- Retries transient failures with backoff
- Skips bad data safely
- Differentiates:
  - API errors
  - Data parsing issues
  - Quota limits

---

### Structured Logging (JSON)
- Fully structured logs for:
  - Processing events
  - Retries
  - Failures
  - Insert counts
- Includes metadata:
  - `run_id`
  - `symbol`
  - `provider`
  - `rows`
  - `attempt`

---

### Rate Limit Handling
- Configurable per provider
- Prevents API throttling

---

## Architecture

ingestion (orchestration)
↓
fetcher (API layer)
↓
db (data access layer)
↓
PostgreSQL














