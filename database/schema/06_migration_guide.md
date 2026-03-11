# Database Migration & Deployment Guide

---

## 1. Pre-Deployment Checklist

### 1.1 Infrastructure Requirements
```
PostgreSQL Version: 13.0+
Minimum Storage: 100GB (initial)
Scalable to: 5TB+ with partitioning
RAM: 32GB+ recommended
CPU: 8+ cores for parallel queries
Backup Storage: 2x database size
```

### 1.2 Configuration Requirements
```postgresql
-- postgresql.conf settings
shared_buffers = 8GB              # 25% of RAM
effective_cache_size = 24GB       # 75% of RAM
work_mem = 100MB                  # (RAM / max_connections) / 4
maintenance_work_mem = 2GB
max_wal_size = 4GB
wal_level = replica               # For replication & recovery
max_wal_senders = 3
wal_keep_size = 1GB
synchronous_commit = remote_apply # For HA

# Enable constraint exclusion for partition optimization
constraint_exclusion = partition

# Connection pooling
max_connections = 200
```

---

## 2. Initial Deployment (MVP - Phase 1)

### 2.1 Step-by-Step Deployment

#### Step 1: Create Database and Extensions
```bash
#!/bin/bash
set -e

DB_NAME="stockexchange"
DB_USER="stockex_app"
DB_PASSWORD="$(openssl rand -base64 32)"

# Create user
createuser --createdb --no-superuser $DB_USER

# Create database
createdb -O $DB_USER $DB_NAME

# Connect and enable extensions
psql -U postgres -d $DB_NAME << EOF
\set ON_ERROR_STOP on

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";    -- For multi-column indexes

-- Set application user permissions
GRANT CREATE ON DATABASE $DB_NAME TO $DB_USER;
GRANT USAGE ON SCHEMA public TO $DB_USER;
GRANT CREATE ON SCHEMA public TO $DB_USER;
EOF

echo "Database credentials:"
echo "Username: $DB_USER"
echo "Password: $DB_PASSWORD"
echo "Database: $DB_NAME"
```

#### Step 2: Create Core Tables
```bash
psql -U $DB_USER -d $DB_NAME -f 01_core_tables.sql
```

**Verification:**
```bash
psql -U $DB_USER -d $DB_NAME << EOF
SELECT schemaname, tablename FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
EOF
```

Expected output: 30+ tables created

#### Step 3: Create Materialized Views
```bash
psql -U $DB_USER -d $DB_NAME -f 03_views_and_queries.sql
```

#### Step 4: Create Stored Procedures
```bash
psql -U $DB_USER -d $DB_NAME -f 04_stored_procedures.sql
```

#### Step 5: Add Initial Data
```bash
psql -U $DB_USER -d $DB_NAME << EOF
-- Insert exchanges
INSERT INTO exchanges (code, name, country, timezone, opening_time, closing_time)
VALUES
    ('NYSE', 'New York Stock Exchange', 'United States', 'America/New_York', '09:30', '16:00'),
    ('NASDAQ', 'NASDAQ', 'United States', 'America/New_York', '09:30', '16:00'),
    ('LSE', 'London Stock Exchange', 'United Kingdom', 'Europe/London', '08:00', '16:30');

-- Insert indicators
INSERT INTO indicators (name, description, calculation_method, parameters)
VALUES
    ('SMA_50', '50-period Simple Moving Average', 'SUM(close) / 50', '{"period": 50}'::JSONB),
    ('RSI_14', '14-period Relative Strength Index', 'Complex momentum', '{"period": 14}'::JSONB),
    ('MACD', 'Moving Average Convergence Divergence', 'Complex trend', '{"fast": 12, "slow": 26, "signal": 9}'::JSONB);
EOF
```

---

## 3. Phase 2 Deployment (Early Scale)

### 3.1 Add Partitioning

```bash
# Wait for transaction volume to exceed 1 month of data
psql -U $DB_USER -d $DB_NAME -f 02_partitioning_strategy.sql
```

**Important:** This creates new partitioned tables. Migrate data:

```bash
psql -U $DB_USER -d $DB_NAME << EOF
\set ON_ERROR_STOP on
BEGIN;

-- Migrate OHLC data to partitioned table
INSERT INTO ohlc_data_partitioned
SELECT * FROM ohlc_data;

-- Verify row count
SELECT
    (SELECT COUNT(*) FROM ohlc_data) as original_count,
    (SELECT COUNT(*) FROM ohlc_data_partitioned) as partitioned_count;

-- If counts match, truncate original
TRUNCATE ohlc_data;

COMMIT;
EOF
```

### 3.2 Switch to Partitioned Tables

```bash
psql -U $DB_USER -d $DB_NAME << EOF
-- Create views for backward compatibility
CREATE OR REPLACE VIEW ohlc_data_v2 AS SELECT * FROM ohlc_data_partitioned;
CREATE OR REPLACE VIEW quotes_v2 AS SELECT * FROM quotes_partitioned;

-- Gradually switch application to read from _partitioned tables
-- Once verified, drop original non-partitioned tables
EOF
```

---

## 4. Zero-Downtime Migration Strategy

### 4.1 For Running Systems

Use logical replication to migrate without downtime:

```bash
# On source (old system)
psql -U postgres << EOF
CREATE ROLE replication_user WITH REPLICATION PASSWORD 'secure_password';
CREATE PUBLICATION stock_exchange FOR ALL TABLES;
EOF

# On target (new system with new schema)
psql -U postgres << EOF
-- Wait for replication subscription to sync
CREATE SUBSCRIPTION stock_exchange_sub
CONNECTION 'dbname=stockexchange user=replication_user password=secure_password host=old_system'
PUBLICATION stock_exchange;

-- Monitor sync progress
SELECT * FROM pg_stat_subscription;
EOF
```

### 4.2 Cutover Procedure

```bash
#!/bin/bash
set -e

# 1. Verify subscriptions are in sync (lag = 0)
psql -U postgres -d stockexchange << EOF
SELECT schemaname, tablename, n_live_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
EOF

# 2. Stop application writes (maintenance window)
# - Set application to read-only mode
# - Wait for in-flight transactions to complete

# 3. Wait for replication to catch up
while true; do
    LAG=$(psql -U postgres -d stockexchange -t -c \
        "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) FROM pg_is_in_recovery();")
    if [ "$LAG" -lt 1 ]; then
        echo "Replication caught up"
        break
    fi
    sleep 1
done

# 4. Drop replication subscription
psql -U postgres -d stockexchange << EOF
DROP SUBSCRIPTION stock_exchange_sub;
ALTER SYSTEM SET synchronous_standby_names = 'standby_name';
SELECT pg_reload_conf();
EOF

# 5. Point application to new system
# - Update connection strings
# - Verify connectivity

# 6. Resume application writes
# - Take system out of read-only mode

echo "Cutover complete at $(date)"
```

---

## 5. Rollback Procedures

### 5.1 Quick Rollback (< 10 minutes)

If issues detected within 10 minutes:

```bash
#!/bin/bash
# Point application back to original database
sed -i 's/new_host/old_host/g' /app/config/database.conf

# Restart application
systemctl restart stockexchange-app

# Verify
curl http://localhost:8080/health
```

### 5.2 Data Rollback (from backup)

If data corruption detected:

```bash
# Find appropriate backup
ls -lh /backups/

# Stop application
systemctl stop stockexchange-app

# Drop corrupted database
dropdb stockexchange

# Restore from backup
pg_restore -d stockexchange /backups/2024_01_15_0200.tar.gz

# Verify integrity
psql -d stockexchange -c "SELECT COUNT(*) FROM users;"

# Restart application
systemctl start stockexchange-app
```

---

## 6. Add Check Constraints

```postgresql
-- These should be added after initial deployment
-- They validate business logic at database level

ALTER TABLE quotes ADD CONSTRAINT chk_quotes_ask_bid
    CHECK (ask_price >= bid_price);

ALTER TABLE positions ADD CONSTRAINT chk_positions_quantity
    CHECK (quantity >= 0);

ALTER TABLE orders ADD CONSTRAINT chk_orders_quantity
    CHECK (quantity > 0);

ALTER TABLE orders ADD CONSTRAINT chk_orders_price
    CHECK (price IS NOT NULL OR order_type = 'market');

ALTER TABLE orders ADD CONSTRAINT chk_orders_stop_limit
    CHECK (
        (order_type != 'stop_limit') OR
        (stop_price IS NOT NULL AND price IS NOT NULL)
    );

ALTER TABLE security_fundamentals ADD CONSTRAINT chk_fundamentals_ratios
    CHECK (
        price_to_earnings IS NULL OR price_to_earnings > 0
    );

ALTER TABLE index_constituents ADD CONSTRAINT chk_constituents_weight
    CHECK (weight >= 0 AND weight <= 1);

ALTER TABLE users ADD CONSTRAINT chk_users_cash_balance
    CHECK (cash_balance >= 0);
```

---

## 7. Performance Tuning Post-Deployment

### 7.1 Analyze Statistics
```bash
psql -U $DB_USER -d $DB_NAME << EOF
-- Update planner statistics
ANALYZE;

-- Check distribution
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
EOF
```

### 7.2 Index Usage Analysis
```bash
psql -U $DB_USER -d $DB_NAME << EOF
-- Find unused indexes
SELECT
    idx.indexname,
    idx.tablename,
    idx.indexdef,
    stat.idx_scan as scans,
    pg_size_pretty(pg_relation_size(idx.indexrelname)) as size
FROM pg_indexes idx
LEFT JOIN pg_stat_user_indexes stat
    ON idx.indexname = stat.indexrelname
WHERE idx.schemaname = 'public'
    AND stat.idx_scan < 100
    AND pg_relation_size(idx.indexrelid) > 1000000  -- > 1MB
ORDER BY pg_relation_size(idx.indexrelid) DESC;
EOF
```

### 7.3 Query Performance Analysis
```bash
psql -U $DB_USER -d $DB_NAME << EOF
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries > 100ms
SELECT pg_reload_conf();

-- After 1 day, analyze slow queries
SELECT
    mean_time,
    calls,
    query
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC
LIMIT 20;
EOF
```

---

## 8. Maintenance & Monitoring Jobs

### 8.1 Setup pg_cron for Automated Maintenance

```bash
# Install pg_cron extension
sudo apt install postgresql-13-cron

psql -U postgres -d stockexchange << EOF
CREATE EXTENSION pg_cron;
GRANT USAGE ON SCHEMA cron TO $DB_USER;
EOF
```

### 8.2 Schedule Maintenance Tasks
```postgresql
-- Refresh materialized views every 5 minutes during market hours
SELECT cron.schedule('refresh-portfolio-mvs', '*/5 9-17 * * 1-5',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_portfolio_summary');

SELECT cron.schedule('refresh-security-mvs', '*/5 9-17 * * 1-5',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_security_performance');

-- Daily maintenance
SELECT cron.schedule('daily-analyze', '0 2 * * *',
    'ANALYZE;');

SELECT cron.schedule('daily-vacuum', '0 3 * * *',
    'VACUUM ANALYZE;');

-- Create next month's partitions
SELECT cron.schedule('create-monthly-partitions', '0 0 1 * *',
    'SELECT create_next_month_partitions();');

-- Archive old OHLC data (quarterly)
SELECT cron.schedule('archive-ohlc-data', '0 4 1 */3 *',
    'SELECT archive_old_ohlc_data();');

-- Clean expired sessions (daily)
SELECT cron.schedule('cleanup-sessions', '0 1 * * *',
    'CALL cleanup_expired_sessions();');

-- Calculate daily portfolio valuations
SELECT cron.schedule('daily-portfolio-valuations', '0 17 * * 1-5',
    'CALL calculate_all_portfolio_valuations();');

-- Check price alerts every minute during market hours
SELECT cron.schedule('check-price-alerts', '* 9-16 * * 1-5',
    'SELECT check_price_alerts();');
```

---

## 9. Monitoring & Alerting

### 9.1 Key Metrics to Monitor

```sql
-- Connection count
SELECT count(*) as total_connections
FROM pg_stat_activity;

-- Active queries
SELECT
    pid,
    usename,
    state,
    query,
    state_change
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY state_change;

-- Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit)  as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;

-- Replication lag
SELECT
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- Partition sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE '%2026%'
ORDER BY tablename;
```

### 9.2 Alert Thresholds

```yaml
alerts:
  - name: high_connection_count
    condition: "total_connections > 180"  # 90% of max_connections
    severity: warning

  - name: low_cache_hit_ratio
    condition: "cache_hit_ratio < 0.98"
    severity: warning

  - name: replication_lag
    condition: "replay_lag > 1s"
    severity: critical

  - name: disk_space_low
    condition: "free_space < 10GB"
    severity: critical

  - name: high_table_bloat
    condition: "dead_tuples_percent > 20%"
    severity: warning

  - name: long_running_query
    condition: "query_duration > 60s"
    severity: warning
```

---

## 10. Troubleshooting Common Issues

### 10.1 High Query Latency

```sql
-- Find slow queries
SELECT
    query,
    calls,
    mean_time,
    max_time,
    stddev_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC
LIMIT 10;

-- Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM positions WHERE user_id = 'xxx' AND quantity > 0;

-- Add missing index if needed
CREATE INDEX idx_positions_user_quantity
ON positions(user_id, quantity);
```

### 10.2 Partition Issues

```sql
-- Check partition constraint exclusion
SET constraint_exclusion = partition;
EXPLAIN SELECT * FROM ohlc_data_partitioned
WHERE open_time > '2026-03-01'::DATE;

-- Manually create missing partition
CREATE TABLE ohlc_data_2026_05_01
PARTITION OF ohlc_data_partitioned
FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- Check partition sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'ohlc_data%'
ORDER BY tablename;
```

### 10.3 Lock Contention

```sql
-- Find long locks
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE pg_blocking_pids(pid)::text != '{}';

-- Kill blocking query if necessary
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE pid = <blocking_pid>;
```

---

## 11. Compliance & Audit

### 11.1 Data Protection

```bash
# Enable SSL for all connections
# In postgresql.conf
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'

# In pg_hba.conf - require SSL
hostssl all stockex_app 0.0.0.0/0 md5
```

### 11.2 Access Audit
```sql
-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id, entity_type, entity_id, action,
        old_values, new_values, ip_address
    ) VALUES (
        current_user_id(),
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id)::TEXT,
        TG_OP,
        to_jsonb(OLD),
        to_jsonb(NEW),
        inet_client_addr()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

---

## 12. Disaster Recovery Procedures

### 12.1 Full Database Restore

```bash
#!/bin/bash
# Time to restore: ~2 hours for 1TB database

# 1. Get latest backup
BACKUP_FILE="/backups/$(ls -t /backups/ | head -1)"
echo "Restoring from $BACKUP_FILE"

# 2. Stop application
systemctl stop stockexchange-app

# 3. Drop old database
dropdb stockexchange

# 4. Restore
pg_restore -d stockexchange "$BACKUP_FILE" -v

# 5. Verify
psql -d stockexchange -c "SELECT COUNT(*) FROM users;"

# 6. Start application
systemctl start stockexchange-app

# 7. Run health checks
curl http://localhost:8080/health
```

### 12.2 Point-in-Time Recovery

```bash
# Stop database cluster
pg_ctl stop -D /var/lib/postgresql/13/main

# Restore base backup
pg_basebackup -D /recovery_dir -Ft -z

# Create recovery.conf
cat > /recovery_dir/recovery.conf << EOF
restore_command = 'cp /wal_archive/%f %p'
recovery_target_timeline = 'latest'
recovery_target_time = '2024-01-15 14:30:00'
EOF

# Start recovery
pg_ctl start -D /recovery_dir
```

---

## 13. Performance Baselines

After deployment, establish baselines:

```
Portfolio Query (user with 20 positions): < 50ms
Quote Insert (bulk 1000): < 100ms
Chart Data Retrieval (1 year): < 300ms
Screener Execution (500 stocks): < 1.5s
Order Execution: < 200ms
Position Update: < 50ms
```

Monitor continuously and investigate regressions.

