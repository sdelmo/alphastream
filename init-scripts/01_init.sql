-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create stock_quotes table
CREATE TABLE IF NOT EXISTS stock_quotes (
    id SERIAL,
    symbol VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    change_percent VARCHAR(20),
    trading_day DATE NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (symbol, fetched_at)
);

-- Convert to hypertable (TimescaleDB magic for time-series data)
SELECT create_hypertable(
    'stock_quotes',
    'fetched_at',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_symbol_time 
    ON stock_quotes (symbol, fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_trading_day 
    ON stock_quotes (trading_day);

-- Verification table (proves init script ran)
CREATE TABLE init_verification (
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO init_verification (message) 
VALUES ('Database initialized successfully at startup!');
