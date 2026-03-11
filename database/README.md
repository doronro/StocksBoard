# Stock Exchange Board - PostgreSQL Database Schema

A comprehensive, production-ready PostgreSQL database schema for a real-time stock exchange board application with support for portfolio management, order execution, watchlists, screeners, and compliance tracking.

## Quick Start

### Prerequisites

- PostgreSQL 13+ installed and running
- psql CLI tool
- Bash shell

### Installation

```bash
# Navigate to database directory
cd database/schema

# Make initialization script executable
chmod +x 00_init_database.sh

# Run initialization for development
./00_init_database.sh development

# Or for production
./00_init_database.sh production
```

This will:
1. Create the database and application user
2. Enable required extensions
3. Create all 30+ tables with proper constraints
4. Create views and stored procedures
5. Insert reference data (exchanges, indicators, indices)
6. Set up partitioning (for production environments)

## Database Architecture

### Core Components

#### 1. **Security & Market Data** (Foundation)
```
securities          → Master stock/security definitions
quotes              → Real-time price quotes (partitioned)
ohlc_data           → Candlestick data for charting (partitioned)
security_fundamentals → Financial metrics (P/E, dividend yield, etc.)
```

**Optimization:**
- Quotes: ~1000 updates/second per security
- OHLC: Pre-aggregated for fast charting
- Fundamentals: Updated daily

#### 2. **User & Account Management**
```
users              → User accounts, status, risk tolerance
user_profiles      → Preferences, theme, notifications
sessions           → Authentication tokens, IP tracking
```

#### 3. **Portfolio Management**
```
positions          → Current holdings (user + security)
portfolio_valuations → Daily snapshots for P&L tracking
transactions       → Trade history, dividends, splits (partitioned)
orders             → Buy/sell orders with execution details
order_executions   → Atomic execution records
```

**Key Features:**
- Automatic position averaging (cost basis)
- Unrealized gain/loss calculation
- Dividend and corporate action handling
- Order status tracking (pending → filled → settled)

#### 4. **Watchlist & Alerts**
```
watchlists         → User-created watchlists
watchlist_items    → Securities in watchlists
price_alerts       → Automated price monitoring
```

#### 5. **Screeners & Analysis**
```
screeners          → Saved stock screening criteria
screening_results  → Latest matching securities
indicators         → Technical indicator definitions
indicator_values   → Calculated indicator values
```

#### 6. **Market Data & News**
```
indices            → Market indices (S&P 500, etc.)
index_constituents → Stocks in each index with weights
index_quotes       → Index price history
news_articles      → Market news with sentiment
earnings_calendar  → Earnings dates and estimates
sec_filings        → SEC filing tracker
```

#### 7. **Audit & Compliance**
```
audit_logs         → All user actions (partitioned)
transaction_audit_trail → Trade execution audit
```

## Table Relationships

### User Portfolio Flow

```
User
  ├── Positions (current holdings)
  │    ├── quantity, average_cost_price, market_value
  │    └── unrealized_gain_loss (auto-calculated)
  │
  ├── Orders (pending trades)
  │    ├── buy/sell orders with limit/market/stop types
  │    └── Order Executions (atomic fills)
  │
  ├── Transactions (completed trades)
  │    ├── buy, sell, dividend, stock_split
  │    └── Historical record for tax reporting
  │
  ├── Portfolio Valuations (daily snapshots)
  │    └── Tracks account growth over time
  │
  └── Watchlists (monitored securities)
       └── Price Alert Triggers
```

### Market Data Flow

```
Security (Master Reference)
  ├── Quotes (real-time, 1-second granularity)
  │    └── Aggregated to OHLC
  │
  ├── OHLC Data (1m, 5m, 15m, 1h, 1d, 1w, 1mo)
  │    └── Used for charting, technical analysis
  │
  ├── Security Fundamentals (daily updates)
  │    ├── market_cap, P/E, dividend_yield
  │    └── Updated during/after market close
  │
  ├── News Articles (with sentiment)
  │    └── Associated via news_security_association
  │
  ├── Earnings Calendar
  │    └── Tracks EPS surprises
  │
  └── In Index Constituents
       └── Weighted positions in market indices
```

## Performance Optimization

### Query Performance Targets

| Operation | Target | Method |
|-----------|--------|--------|
| Portfolio Summary | <100ms | Materialized view (mv_portfolio_summary) |
| Quote Insert | <1ms | Partitioned table, batch inserts |
| Chart Data (1 year) | <500ms | Pre-aggregated OHLC, partitioning |
| Screener Execution | <2s | Pre-filtered MV + JSONB criteria |
| Position Update | <50ms | Indexed by (user_id, security_id) |
| Order Execution | <200ms | Stored procedure with atomic operations |

### Key Indexes

**Hot Paths:**
```sql
-- Portfolio queries
idx_positions_user_id (user_id)
idx_positions_user_id_security_id (user_id, security_id)

-- Quote streaming
idx_quotes_security_id_timestamp (security_id, timestamp DESC)

-- Order management
idx_orders_user_id_status (user_id, status)

-- Chart data
idx_ohlc_data_security_period_time (security_id, period, open_time DESC)

-- Market data
idx_securities_symbol (symbol)
idx_security_fundamentals_security_id (security_id)
```

### Materialized Views

Auto-refreshed every 5 minutes during market hours:

```sql
mv_portfolio_summary       -- User account summary
mv_security_performance    -- Current market data with changes
```

## Data Partitioning

### Partitioning Strategy

Partitioning significantly improves performance for large datasets:

| Table | Partition Key | Interval | Retention |
|-------|---------------|----------|-----------|
| quotes | timestamp (daily) | 1 day | 1 month |
| ohlc_data | open_time (monthly) | 1 month | 3 years |
| transactions | transaction_date (annual) | 1 year | Indefinite |
| audit_logs | created_at (monthly) | 1 month | 2 years |

**Benefits:**
- Partition elimination (scans only relevant partitions)
- Easier archival of old data
- Parallel sequential scans
- Better index locality

### Example: Querying OHLC Data

```sql
-- Query automatically scans only March 2026 partition
SELECT * FROM ohlc_data
WHERE security_id = 1 AND period = '1d'
  AND open_time BETWEEN '2026-03-01' AND '2026-03-31';
```

## Stored Procedures

Core business logic implemented as stored procedures for atomicity:

### Portfolio Operations
```sql
-- Execute order with position update
SELECT execute_market_order(order_id, quantity, price, timestamp);

-- Calculate portfolio valuation
SELECT calculate_portfolio_valuation(user_id);

-- Process all user valuations
CALL calculate_all_portfolio_valuations();
```

### Account Operations
```sql
-- Deposit funds
SELECT deposit_funds(user_id, amount, reference);

-- Withdraw funds
SELECT withdraw_funds(user_id, amount, reference);
```

### Corporate Actions
```sql
-- Record dividend payment to all holders
SELECT record_dividend_payment(security_id, dividend_per_share, date);

-- Handle stock split
SELECT process_stock_split(security_id, split_ratio, date);
```

### Watchlist Management
```sql
-- Add security to watchlist
SELECT add_to_watchlist(user_id, symbol, watchlist_id);

-- Remove from watchlist
SELECT remove_from_watchlist(watchlist_item_id);
```

### Monitoring
```sql
-- Check triggered price alerts
SELECT check_price_alerts();

-- Record screener results
SELECT record_screening_results(screener_id, security_ids_array);
```

## Data Integrity

### Constraints

**Primary Keys:** UUIDs for user-facing records, serial/bigserial for internal

**Foreign Keys:** All use ON DELETE CASCADE except audit_logs (SET NULL)

**Unique Constraints:**
```sql
UNIQUE(securities.symbol)
UNIQUE(users.email)
UNIQUE(watchlist_items.watchlist_id, security_id)
UNIQUE(positions.user_id, security_id) WHERE quantity > 0
```

**Check Constraints (recommended to add post-deployment):**
```sql
CHECK (ask_price >= bid_price)          -- Quotes
CHECK (quantity >= 0)                   -- Positions
CHECK (quantity > 0)                    -- Orders
```

### Audit Logging

All critical operations logged automatically:
- User login/logout
- Order creation, execution, cancellation
- Position changes
- Account deposits/withdrawals
- System configuration changes

## Views

### User-Facing Views

```sql
v_user_portfolio_summary    -- Total account value, returns
v_user_positions_detailed   -- Holdings with current market prices
v_user_orders_status        -- Order status with fill details
v_watchlist_performance     -- Watchlist items with prices
v_user_trading_activity     -- Transaction history by period
```

### Market Data Views

```sql
v_security_market_data      -- Current prices, 52-week range, technicals
v_sector_performance        -- Sector aggregates
v_index_performance         -- Index values and constituents
v_upcoming_earnings         -- Earnings calendar
```

### Alert & Screening Views

```sql
v_active_price_alerts       -- Alerts with current status
v_screener_results_latest   -- Latest screening runs
v_screener_results_with_data-- Results with market data
```

### Compliance Views

```sql
v_user_login_activity       -- Login history and locations
v_suspicious_activity       -- Anomaly detection
```

## Migration & Deployment

### Quick Start (Development)

```bash
./00_init_database.sh development
```

### Production Deployment

```bash
# 1. Initialize database
./00_init_database.sh production

# 2. Enable SSL in postgresql.conf
ssl = on

# 3. Configure pg_hba.conf for remote connections
hostssl all stockex_app 10.0.0.0/8 md5

# 4. Set up automated maintenance jobs
psql -d stockexchange << EOF
CREATE EXTENSION pg_cron;
SELECT cron.schedule('daily-analyze', '0 2 * * *', 'ANALYZE;');
SELECT cron.schedule('daily-vacuum', '0 3 * * *', 'VACUUM ANALYZE;');
EOF

# 5. Configure monitoring (see migration_guide.md)
```

### Rollback Procedures

See `06_migration_guide.md` for detailed rollback procedures:
- Quick rollback (switch connection)
- Data rollback (from backup)
- Point-in-time recovery

## Monitoring

### Key Metrics

```sql
-- Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_ratio
FROM pg_statio_user_tables;

-- Query performance
SELECT query, mean_time, calls FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;

-- Connection count
SELECT count(*) FROM pg_stat_activity;
```

### Alert Thresholds

- Connection count > 180/200 (90% of max)
- Cache hit ratio < 98%
- Query duration > 60 seconds
- Disk space < 10GB
- Replication lag > 1 second

## Configuration

### Connection String

```
postgresql://stockex_app:password@localhost:5432/stockexchange?sslmode=require
```

### Environment Variables

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stockexchange
DB_USER=stockex_app
DB_PASSWORD=<generated>
```

## File Structure

```
database/
├── schema/
│   ├── 00_init_database.sh          # Main initialization script
│   ├── 01_core_tables.sql           # All table definitions
│   ├── 02_partitioning_strategy.sql # Partitioning setup
│   ├── 03_views_and_queries.sql     # Views and query helpers
│   ├── 04_stored_procedures.sql     # Business logic procedures
│   ├── 05_erd_and_design_docs.md    # Architecture documentation
│   └── 06_migration_guide.md        # Deployment procedures
└── README.md                         # This file
```

## Documentation

- **05_erd_and_design_docs.md** - Complete ERD, schema design decisions, query examples
- **06_migration_guide.md** - Phase-by-phase deployment, rollback, monitoring

## Performance Tuning

### PostgreSQL Configuration

```ini
shared_buffers = 8GB                # 25% of RAM
effective_cache_size = 24GB         # 75% of RAM
work_mem = 100MB
maintenance_work_mem = 2GB
max_wal_size = 4GB
constraint_exclusion = partition    # Enable partition elimination
```

### Maintenance

```bash
# Daily during off-hours
VACUUM ANALYZE;

# Weekly
REINDEX;

# Monthly
CLUSTER;
```

## Troubleshooting

### High Query Latency

```sql
-- Find slow queries
SELECT query, mean_time FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;

-- Get execution plan
EXPLAIN ANALYZE SELECT ...
```

### Partition Issues

```sql
-- Check partition constraint exclusion
SET constraint_exclusion = partition;
EXPLAIN SELECT * FROM ohlc_data WHERE open_time > '2026-03-01'::DATE;

-- Create missing partition
CREATE TABLE ohlc_data_2026_05_01
PARTITION OF ohlc_data_partitioned
FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
```

### Lock Contention

```sql
-- Find blocking queries
SELECT pid, usename, query, wait_event_type
FROM pg_stat_activity
WHERE pg_blocking_pids(pid)::text != '{}';

-- Kill if necessary
SELECT pg_terminate_backend(pid);
```

## Support

For questions or issues:

1. Check the ERD and schema documentation
2. Review the stored procedure signatures
3. Consult the migration guide for deployment issues
4. Check PostgreSQL logs: `/var/log/postgresql/postgresql.log`

## License

Proprietary - Stock Exchange Board Application

## Compliance

- SOC 2 compliant audit logging
- PCI DSS compatible (no payment processing)
- GDPR ready (user deletion cascades)
- Immutable audit trail (append-only)
