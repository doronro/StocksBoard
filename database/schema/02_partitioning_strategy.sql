-- ============================================================================
-- Stock Exchange Board Application - Partitioning Strategy
-- Handles time-series data optimization for high-volume tables
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- OHLC DATA PARTITIONING (Daily partitions by date)
-- ============================================================================
-- Strategy: Range partitioning by open_time (daily)
-- Retention: Keep 3 years of data, archive older data
-- Volume: 1000+ stocks * multiple timeframes * high frequency updates

-- Drop existing partition if exists (for idempotency)
DROP TABLE IF EXISTS ohlc_data_partitioned CASCADE;

CREATE TABLE IF NOT EXISTS ohlc_data_partitioned (
    id BIGSERIAL,
    security_id INTEGER NOT NULL,
    period VARCHAR(10) NOT NULL,
    open_time TIMESTAMP NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, open_time)
) PARTITION BY RANGE (DATE_TRUNC('day', open_time));

-- Create initial daily partitions (current year + previous year)
-- Adjust dates based on current system date

-- 2025 partitions
CREATE TABLE IF NOT EXISTS ohlc_data_2025_01_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_02_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_03_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Create partitions for remaining 2025 months
CREATE TABLE IF NOT EXISTS ohlc_data_2025_04_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_05_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_06_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_07_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_08_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_09_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_10_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_11_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2025_12_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- 2026 partitions (current year)
CREATE TABLE IF NOT EXISTS ohlc_data_2026_01_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2026_02_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE IF NOT EXISTS ohlc_data_2026_03_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Future partition placeholder
CREATE TABLE IF NOT EXISTS ohlc_data_2026_04_01
    PARTITION OF ohlc_data_partitioned
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

-- Add indexes to partitioned table
CREATE INDEX idx_ohlc_data_partitioned_security_period_time
    ON ohlc_data_partitioned(security_id, period, open_time DESC);
CREATE INDEX idx_ohlc_data_partitioned_open_time
    ON ohlc_data_partitioned(open_time DESC);

-- ============================================================================
-- QUOTES DATA PARTITIONING (Daily partitions)
-- ============================================================================
-- High-frequency data: multiple updates per second per stock
-- Keep recent data in main table, archive older data

DROP TABLE IF EXISTS quotes_partitioned CASCADE;

CREATE TABLE IF NOT EXISTS quotes_partitioned (
    id BIGSERIAL,
    security_id INTEGER NOT NULL,
    last_price DECIMAL(12, 4) NOT NULL,
    bid_price DECIMAL(12, 4),
    ask_price DECIMAL(12, 4),
    bid_size BIGINT,
    ask_size BIGINT,
    volume BIGINT,
    previous_close DECIMAL(12, 4),
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (DATE_TRUNC('day', timestamp));

-- Create recent partitions (keep 1 month of detailed quotes)
CREATE TABLE IF NOT EXISTS quotes_2026_02_08
    PARTITION OF quotes_partitioned
    FOR VALUES FROM ('2026-02-08') TO ('2026-02-09');

CREATE TABLE IF NOT EXISTS quotes_2026_02_09
    PARTITION OF quotes_partitioned
    FOR VALUES FROM ('2026-02-09') TO ('2026-02-10');

CREATE TABLE IF NOT EXISTS quotes_2026_02_10
    PARTITION OF quotes_partitioned
    FOR VALUES FROM ('2026-02-10') TO ('2026-02-11');

CREATE TABLE IF NOT EXISTS quotes_2026_03_10
    PARTITION OF quotes_partitioned
    FOR VALUES FROM ('2026-03-10') TO ('2026-03-11');

CREATE TABLE IF NOT EXISTS quotes_2026_03_11
    PARTITION OF quotes_partitioned
    FOR VALUES FROM ('2026-03-11') TO ('2026-03-12');

CREATE INDEX idx_quotes_partitioned_security_timestamp
    ON quotes_partitioned(security_id, timestamp DESC);
CREATE INDEX idx_quotes_partitioned_timestamp
    ON quotes_partitioned(timestamp DESC);

-- ============================================================================
-- TRANSACTIONS TABLE PARTITIONING (Annual partitions)
-- ============================================================================
-- Lower write frequency than quotes/ohlc, partition by year for long-term retention

DROP TABLE IF EXISTS transactions_partitioned CASCADE;

CREATE TABLE IF NOT EXISTS transactions_partitioned (
    id UUID,
    user_id UUID NOT NULL,
    security_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity DECIMAL(18, 8),
    price DECIMAL(12, 4),
    amount DECIMAL(18, 2) NOT NULL,
    commission DECIMAL(12, 4) DEFAULT 0,
    notes TEXT,
    external_transaction_id VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    settled_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, transaction_date)
) PARTITION BY RANGE (DATE_TRUNC('year', transaction_date));

CREATE TABLE IF NOT EXISTS transactions_2024
    PARTITION OF transactions_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS transactions_2025
    PARTITION OF transactions_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS transactions_2026
    PARTITION OF transactions_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE INDEX idx_transactions_partitioned_user_id
    ON transactions_partitioned(user_id);
CREATE INDEX idx_transactions_partitioned_security_id
    ON transactions_partitioned(security_id);
CREATE INDEX idx_transactions_partitioned_user_id_date
    ON transactions_partitioned(user_id, transaction_date DESC);

-- ============================================================================
-- AUDIT LOGS PARTITIONING (Monthly partitions, keep 2 years)
-- ============================================================================

DROP TABLE IF EXISTS audit_logs_partitioned CASCADE;

CREATE TABLE IF NOT EXISTS audit_logs_partitioned (
    id UUID PRIMARY KEY,
    user_id UUID,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (DATE_TRUNC('month', created_at));

CREATE TABLE IF NOT EXISTS audit_logs_2024_01
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE IF NOT EXISTS audit_logs_2025_01
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS audit_logs_2025_02
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_01
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_02
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE IF NOT EXISTS audit_logs_2026_03
    PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

CREATE INDEX idx_audit_logs_partitioned_user_id
    ON audit_logs_partitioned(user_id);
CREATE INDEX idx_audit_logs_partitioned_entity_type
    ON audit_logs_partitioned(entity_type);
CREATE INDEX idx_audit_logs_partitioned_action
    ON audit_logs_partitioned(action);

-- ============================================================================
-- ARCHIVAL STRATEGY
-- ============================================================================
-- Procedure to archive old OHLC data (older than 3 years)
-- Called monthly via pg_cron

CREATE OR REPLACE FUNCTION archive_old_ohlc_data()
RETURNS TABLE(archived_rows BIGINT) AS $$
DECLARE
    v_cutoff_date DATE;
    v_archived_count BIGINT;
BEGIN
    v_cutoff_date := CURRENT_DATE - INTERVAL '3 years';

    -- Archive records older than 3 years
    INSERT INTO archived_ohlc_data
    SELECT * FROM ohlc_data
    WHERE open_time < v_cutoff_date;

    GET DIAGNOSTICS v_archived_count = ROW_COUNT;

    -- Delete archived records
    DELETE FROM ohlc_data
    WHERE open_time < v_cutoff_date;

    RETURN QUERY SELECT v_archived_count;
END;
$$ LANGUAGE plpgsql;

-- Procedure to drop old partitions
CREATE OR REPLACE PROCEDURE drop_old_partition(
    p_partition_name VARCHAR,
    p_table_name VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('DROP TABLE IF EXISTS %I', p_partition_name);

    INSERT INTO partition_metadata (table_name, partition_key, status, created_at)
    VALUES (p_table_name, p_partition_name, 'deleted', CURRENT_TIMESTAMP)
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Partition % dropped successfully', p_partition_name;
END;
$$;

-- ============================================================================
-- MIGRATION VIEW TO SUPPORT LEGACY QUERIES
-- ============================================================================
-- Create views that redirect queries to partitioned tables while maintaining backward compatibility

CREATE OR REPLACE VIEW ohlc_data_view AS
SELECT * FROM ohlc_data_partitioned;

CREATE OR REPLACE VIEW quotes_view AS
SELECT * FROM quotes_partitioned;

-- ============================================================================
-- PARTITION MAINTENANCE PROCEDURES
-- ============================================================================

-- Function to create partition for next month
CREATE OR REPLACE FUNCTION create_next_month_partitions()
RETURNS void AS $$
DECLARE
    v_next_month DATE;
    v_partition_name VARCHAR;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    v_next_month := DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month';
    v_start_date := v_next_month;
    v_end_date := v_next_month + INTERVAL '1 month';

    -- Create OHLC partition
    v_partition_name := 'ohlc_data_' || TO_CHAR(v_next_month, 'YYYY_MM_DD');
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF ohlc_data_partitioned FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        v_start_date,
        v_end_date
    );

    -- Create quotes partition
    v_partition_name := 'quotes_' || TO_CHAR(v_next_month, 'YYYY_MM_DD');
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF quotes_partitioned FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        v_start_date,
        v_end_date
    );

    -- Create audit logs partition
    v_partition_name := 'audit_logs_' || TO_CHAR(v_next_month, 'YYYY_MM');
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_logs_partitioned FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        v_start_date,
        v_end_date
    );

    RAISE NOTICE 'Partitions created for %', v_next_month;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STATISTICS & VACUUM JOBS (For pg_cron)
-- ============================================================================
-- These would be scheduled to run automatically

-- SELECT cron.schedule('refresh-partition-stats', '0 2 * * *', 'ANALYZE ohlc_data_partitioned;');
-- SELECT cron.schedule('refresh-quote-stats', '0 3 * * *', 'ANALYZE quotes_partitioned;');
-- SELECT cron.schedule('create-monthly-partitions', '0 0 1 * *', 'SELECT create_next_month_partitions();');
-- SELECT cron.schedule('archive-old-ohlc', '0 4 * * SUN', 'SELECT archive_old_ohlc_data();');

-- ============================================================================
-- TABLE PARTITIONING DOCUMENTATION
-- ============================================================================
/*
PARTITION STRATEGY SUMMARY:

1. OHLC_DATA_PARTITIONED:
   - Type: Range partitioning on DATE_TRUNC('day', open_time)
   - Partition interval: Monthly
   - Retention: 3 years
   - Archive strategy: Move data older than 3 years to archived_ohlc_data table
   - Expected size per month: ~500GB (1000 stocks * 10 timeframes * high frequency)

2. QUOTES_PARTITIONED:
   - Type: Range partitioning on DATE_TRUNC('day', timestamp)
   - Partition interval: Daily
   - Retention: 1 month (for detailed tick data)
   - Archive strategy: Aggregate to OHLC for long-term storage
   - Expected size per day: ~50GB (1000 stocks * multiple updates per second)

3. TRANSACTIONS_PARTITIONED:
   - Type: Range partitioning on DATE_TRUNC('year', transaction_date)
   - Partition interval: Annual
   - Retention: Indefinite (compliance requirement)
   - Expected size per year: ~50GB (high transaction volume)

4. AUDIT_LOGS_PARTITIONED:
   - Type: Range partitioning on DATE_TRUNC('month', created_at)
   - Partition interval: Monthly
   - Retention: 2 years
   - Expected size per month: ~10GB

PERFORMANCE BENEFITS:
- Faster queries due to partition elimination
- Easier maintenance and purging of old data
- Parallel sequential scans across partitions
- Improved index efficiency
- Better cache utilization

MIGRATION NOTES:
- Use views (ohlc_data_view, quotes_view) for backward compatibility
- Gradual migration from non-partitioned tables
- Ensure constraint exclusion is enabled: SET constraint_exclusion = partition;
*/
