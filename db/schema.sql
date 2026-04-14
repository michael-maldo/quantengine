set search_path to prod,public;
drop table if exists prices;
drop table if exists features;
drop table if exists fundamentals;
drop table if exists symbols;
drop schema if exists prod;
-- drop database if exists quantengine;


CREATE SCHEMA IF NOT EXISTS prod;

CREATE TABLE IF NOT EXISTS prod.symbols (
    symbol TEXT NOT NULL,
    name TEXT,
    exchange TEXT,
    currency TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT symbols_pkey PRIMARY KEY (symbol)
);

CREATE TABLE IF NOT EXISTS prod.prices(
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES prod.symbols(symbol)
);

CREATE INDEX idx_prices_date ON prod.prices(date);

CREATE TABLE IF NOT EXISTS prod.features (
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    close DOUBLE PRECISION,
    volume BIGINT,
    return_1d DOUBLE PRECISION,
    return_5d DOUBLE PRECISION,
    sma20 DOUBLE PRECISION,
    sma50 DOUBLE PRECISION,
    price_to_sma20 DOUBLE PRECISION,
    rsi14 DOUBLE PRECISION,
    volatility20 DOUBLE PRECISION,
    volume_ratio DOUBLE PRECISION,
    momentum252 DOUBLE PRECISION,
    drawdown DOUBLE PRECISION,
    pe_ratio DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),

    CONSTRAINT features_pkey PRIMARY KEY (symbol, date),

    CONSTRAINT features_symbol_fkey
        FOREIGN KEY (symbol)
        REFERENCES prod.symbols(symbol)
);


CREATE TABLE IF NOT EXISTS prod.fundamentals (
    symbol TEXT NOT NULL,
    report_date DATE NOT NULL,
    eps NUMERIC,
    revenue BIGINT,
    net_income BIGINT,
    shares_outstanding BIGINT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),

    CONSTRAINT fundamentals_pkey PRIMARY KEY (symbol, report_date),

    CONSTRAINT fundamentals_symbol_fkey
        FOREIGN KEY (symbol)
        REFERENCES prod.symbols(symbol)
);

-- CREATE TABLE IF NOT EXISTS prices (
--     id SERIAL PRIMARY KEY,
--     symbol VARCHAR(10) NOT NULL,
--     date DATE NOT NULL,
--     open NUMERIC,
--     high NUMERIC,
--     low NUMERIC,
--     close NUMERIC,
--     volume BIGINT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE INDEX idx_symbol_date ON prices(symbol, date);
