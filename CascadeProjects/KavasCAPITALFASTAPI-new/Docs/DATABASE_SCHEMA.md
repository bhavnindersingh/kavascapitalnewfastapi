# Database Schema for NIFTY 50 Trading System

## Overview

This document defines the complete database schema for our HFT system. The schema is designed to handle:
- High-frequency tick data
- Option chain data
- Market depth information
- VIX data
- System metadata and monitoring

## Core Tables

### 1. Instruments
```sql
CREATE TABLE instruments (
    instrument_token BIGINT PRIMARY KEY,
    tradingsymbol VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    instrument_type VARCHAR(20) NOT NULL,
    segment VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    strike DECIMAL(10, 2),
    lot_size INTEGER,
    expiry TIMESTAMP WITH TIME ZONE,
    option_type VARCHAR(2), -- 'CE' or 'PE'
    tick_size DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tradingsymbol, exchange)
);

CREATE INDEX idx_instruments_symbol ON instruments(tradingsymbol);
CREATE INDEX idx_instruments_expiry ON instruments(expiry);
CREATE INDEX idx_instruments_type ON instruments(instrument_type);
```

### 2. Tick Data
```sql
-- Partitioned by date for better performance
CREATE TABLE tick_data (
    instrument_token BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    last_price DECIMAL(10, 2) NOT NULL,
    volume INTEGER NOT NULL,
    buy_quantity INTEGER,
    sell_quantity INTEGER,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    change DECIMAL(10, 2),
    oi INTEGER, -- Open Interest
    oi_day_high INTEGER,
    oi_day_low INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (instrument_token, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions
CREATE TABLE tick_data_current PARTITION OF tick_data
    FOR VALUES FROM (CURRENT_DATE) TO (CURRENT_DATE + INTERVAL '1 day');

CREATE TABLE tick_data_history PARTITION OF tick_data
    FOR VALUES FROM (MINVALUE) TO (CURRENT_DATE);

-- Indexes
CREATE INDEX idx_tick_data_timestamp ON tick_data(timestamp);
CREATE INDEX idx_tick_data_instrument_timestamp ON tick_data(instrument_token, timestamp);
```

### 3. Market Depth
```sql
CREATE TABLE market_depth (
    id SERIAL PRIMARY KEY,
    instrument_token BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    depth_level INTEGER NOT NULL, -- 1 to 5
    buy_price DECIMAL(10, 2),
    buy_quantity INTEGER,
    buy_orders INTEGER,
    sell_price DECIMAL(10, 2),
    sell_quantity INTEGER,
    sell_orders INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (instrument_token, timestamp, depth_level)
) PARTITION BY RANGE (timestamp);

-- Create partitions
CREATE TABLE market_depth_current PARTITION OF market_depth
    FOR VALUES FROM (CURRENT_DATE) TO (CURRENT_DATE + INTERVAL '1 day');

CREATE TABLE market_depth_history PARTITION OF market_depth
    FOR VALUES FROM (MINVALUE) TO (CURRENT_DATE);

-- Indexes
CREATE INDEX idx_market_depth_instrument ON market_depth(instrument_token);
CREATE INDEX idx_market_depth_timestamp ON market_depth(timestamp);
CREATE INDEX idx_market_depth_instrument_time_level ON market_depth(instrument_token, timestamp, depth_level);
```

### 4. Option Chain
```sql
CREATE TABLE option_chain (
    id SERIAL PRIMARY KEY,
    underlying_token BIGINT NOT NULL, -- NIFTY50 token
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    strike_price DECIMAL(10, 2) NOT NULL,
    expiry TIMESTAMP WITH TIME ZONE NOT NULL,
    ce_token BIGINT,
    ce_oi INTEGER,
    ce_volume INTEGER,
    ce_last_price DECIMAL(10, 2),
    ce_change DECIMAL(10, 2),
    ce_iv DECIMAL(10, 4), -- Implied Volatility
    pe_token BIGINT,
    pe_oi INTEGER,
    pe_volume INTEGER,
    pe_last_price DECIMAL(10, 2),
    pe_change DECIMAL(10, 2),
    pe_iv DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (underlying_token, timestamp, strike_price, expiry)
) PARTITION BY RANGE (timestamp);

-- Create partitions
CREATE TABLE option_chain_current PARTITION OF option_chain
    FOR VALUES FROM (CURRENT_DATE) TO (CURRENT_DATE + INTERVAL '1 day');

CREATE TABLE option_chain_history PARTITION OF option_chain
    FOR VALUES FROM (MINVALUE) TO (CURRENT_DATE);

-- Indexes
CREATE INDEX idx_option_chain_strike ON option_chain(strike_price);
CREATE INDEX idx_option_chain_expiry ON option_chain(expiry);
CREATE INDEX idx_option_chain_timestamp ON option_chain(timestamp);
```

### 5. VIX Data
```sql
CREATE TABLE vix_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    change DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    open DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume INTEGER,
    trend VARCHAR(10), -- 'UP', 'DOWN', 'STABLE'
    regime VARCHAR(20), -- 'LOW', 'NORMAL', 'HIGH', 'EXTREME'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions
CREATE TABLE vix_data_current PARTITION OF vix_data
    FOR VALUES FROM (CURRENT_DATE) TO (CURRENT_DATE + INTERVAL '1 day');

CREATE TABLE vix_data_history PARTITION OF vix_data
    FOR VALUES FROM (MINVALUE) TO (CURRENT_DATE);

-- Indexes
CREATE INDEX idx_vix_data_timestamp ON vix_data(timestamp);
CREATE INDEX idx_vix_data_regime ON vix_data(regime);
```

## Data Integrity Tables

### 1. Data Gaps
```sql
CREATE TABLE data_gaps (
    gap_id SERIAL PRIMARY KEY,
    instrument_token BIGINT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    gap_duration INTERVAL NOT NULL,
    gap_type VARCHAR(20) NOT NULL, -- 'TICK', 'MARKET_DEPTH', 'VIX'
    recovery_status VARCHAR(20) NOT NULL, -- 'PENDING', 'IN_PROGRESS', 'RECOVERED', 'FAILED'
    recovery_method VARCHAR(50), -- 'HISTORICAL_API', 'INTERPOLATION', 'MANUAL'
    recovery_attempts INTEGER DEFAULT 0,
    last_attempt_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_gaps_instrument ON data_gaps(instrument_token);
CREATE INDEX idx_data_gaps_time ON data_gaps(start_time, end_time);
```

### 2. Data Quality Metrics
```sql
CREATE TABLE data_quality_metrics (
    id SERIAL PRIMARY KEY,
    instrument_token BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'TICK', 'MARKET_DEPTH', 'VIX'
    completeness_score DECIMAL(5, 2), -- Percentage of expected data points
    accuracy_score DECIMAL(5, 2), -- Based on validation rules
    latency_ms INTEGER, -- Data arrival latency
    anomaly_count INTEGER,
    anomaly_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_quality_instrument ON data_quality_metrics(instrument_token);
CREATE INDEX idx_data_quality_timestamp ON data_quality_metrics(timestamp);
```

### 3. System Metrics
```sql
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10, 2) NOT NULL,
    component VARCHAR(50) NOT NULL, -- 'WEBSOCKET', 'DATABASE', 'API'
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_system_metrics_component ON system_metrics(component);
```

## Cascade Rules
```sql
-- Add cascade rules for data integrity
ALTER TABLE market_depth
    ADD CONSTRAINT fk_market_depth_instrument
    FOREIGN KEY (instrument_token)
    REFERENCES instruments(instrument_token)
    ON DELETE CASCADE;
```

## Optimized Indexes
```sql
-- Composite indexes for common queries
CREATE INDEX idx_market_depth_instrument_time_level ON market_depth(instrument_token, timestamp, depth_level);
CREATE INDEX idx_tick_data_instrument_time_price ON tick_data(instrument_token, timestamp, last_price);

-- Partial index for recent data
CREATE INDEX idx_tick_data_recent ON tick_data(timestamp, last_price)
WHERE timestamp >= NOW() - INTERVAL '1 day';
```

## Maintenance Functions

### 1. Partition Management
```sql
-- Function to create next day's partitions
CREATE OR REPLACE FUNCTION create_next_day_partitions()
RETURNS void AS $$
BEGIN
    -- Create tick_data partition
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS tick_data_%s PARTITION OF tick_data
        FOR VALUES FROM (%L) TO (%L)',
        to_char(CURRENT_DATE + interval '1 day', 'YYYYMMDD'),
        CURRENT_DATE + interval '1 day',
        CURRENT_DATE + interval '2 days'
    );

    -- Create market_depth partition
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS market_depth_%s PARTITION OF market_depth
        FOR VALUES FROM (%L) TO (%L)',
        to_char(CURRENT_DATE + interval '1 day', 'YYYYMMDD'),
        CURRENT_DATE + interval '1 day',
        CURRENT_DATE + interval '2 days'
    );

    -- Create option_chain partition
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS option_chain_%s PARTITION OF option_chain
        FOR VALUES FROM (%L) TO (%L)',
        to_char(CURRENT_DATE + interval '1 day', 'YYYYMMDD'),
        CURRENT_DATE + interval '1 day',
        CURRENT_DATE + interval '2 days'
    );

    -- Create vix_data partition
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS vix_data_%s PARTITION OF vix_data
        FOR VALUES FROM (%L) TO (%L)',
        to_char(CURRENT_DATE + interval '1 day', 'YYYYMMDD'),
        CURRENT_DATE + interval '1 day',
        CURRENT_DATE + interval '2 days'
    );
END;
$$ LANGUAGE plpgsql;

-- Schedule the function to run daily
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('0 0 * * *', 'SELECT create_next_day_partitions()');
```

### 2. Data Retention
```sql
-- Function to archive old data
CREATE OR REPLACE FUNCTION archive_old_data(days_to_keep INTEGER)
RETURNS void AS $$
DECLARE
    archive_date DATE;
BEGIN
    archive_date := CURRENT_DATE - days_to_keep;

    -- Archive tick data
    INSERT INTO tick_data_archive
    SELECT * FROM tick_data
    WHERE timestamp < archive_date;

    -- Delete archived data
    DELETE FROM tick_data
    WHERE timestamp < archive_date;

    -- Repeat for other tables...
END;
$$ LANGUAGE plpgsql;
```

## Performance Considerations

1. **Partitioning Strategy**
   - All time-series tables are partitioned by date
   - Current day's data in separate partition for faster access
   - Historical data in separate partitions for efficient archival

2. **Indexing Strategy**
   - Timestamp-based indexes for time-series queries
   - Composite indexes for common query patterns
   - Partial indexes for frequently accessed recent data

3. **Data Retention**
   - Automated archival of old data
   - Configurable retention periods
   - Compressed storage for historical data

4. **Batch Processing**
   - Bulk insert capabilities for tick data
   - Efficient update mechanisms for market depth
   - Optimized query patterns for analytics

5. **Monitoring**
   - Table size monitoring
   - Index usage tracking
   - Query performance metrics
   - Partition management alerts
