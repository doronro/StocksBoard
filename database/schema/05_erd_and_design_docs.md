# Stock Exchange Board Database Schema
## Entity Relationship Diagram & Design Documentation

---

## 1. Schema Overview

This PostgreSQL schema supports a comprehensive stock exchange board application with support for:
- Real-time market data and quotes
- User account and portfolio management
- Order execution and settlement
- Watchlist and screener functionality
- News and sentiment analysis
- Technical indicators and charting
- Compliance and audit logging

**Database Size Estimates (at scale):**
- Quotes table: ~50GB per day (1000 stocks * high frequency)
- OHLC data: ~500GB per month
- Transactions: ~50GB per year
- Total active schema: ~1TB (with partitioning and archival)

---

## 2. Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REFERENCE TABLES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐        ┌──────────────────┐                      │
│  │    exchanges     │        │   indicators     │                      │
│  ├──────────────────┤        ├──────────────────┤                      │
│  │ id (PK)          │        │ id (PK)          │                      │
│  │ code (UNIQUE)    │        │ name (UNIQUE)    │                      │
│  │ name             │        │ description      │                      │
│  │ country          │        │ parameters       │                      │
│  │ timezone         │        └──────────────────┘                      │
│  │ opening_time     │                                                  │
│  │ closing_time     │                                                  │
│  │ is_active        │                                                  │
│  └──────────────────┘                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY & MARKET DATA CORE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐                                              │
│  │     securities       │◄─────────1:N─────────┐                      │
│  ├──────────────────────┤                       │                      │
│  │ id (PK)              │                       │                      │
│  │ symbol (UNIQUE)      │                    ┌─────────────────────┐  │
│  │ isin (UNIQUE)        │                    │ security_fundamentals│  │
│  │ cusip (UNIQUE)       │                    ├─────────────────────┤  │
│  │ name                 │                    │ id (PK)             │  │
│  │ exchange_id (FK)─────┼───────────────────►│ security_id (FK,UQ) │  │
│  │ asset_class          │                    │ market_cap          │  │
│  │ sector               │                    │ earnings_per_share  │  │
│  │ industry             │                    │ price_to_earnings   │  │
│  │ currency_code        │                    │ dividend_yield      │  │
│  │ status               │                    │ 52w_high/low        │  │
│  │ listing_date         │                    │ avg_volume_*        │  │
│  │ delisting_date       │                    │ beta                │  │
│  │ is_etf               │                    │ roe, debt_to_equity │  │
│  └──────────────────────┘                    └─────────────────────┘  │
│         │                                                               │
│         │                                                               │
│     1:N │                                                               │
│         ├─────────────────┬─────────────────────┬──────────────────┐  │
│         │                 │                     │                  │  │
│         ▼                 ▼                     ▼                  ▼  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐
│  │    quotes    │  │  ohlc_data   │  │index_constituents│ news_security_│
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │ association  │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)      │  ├────────────┤
│  │ security_id  │  │ security_id  │  │ index_id (FK)│  │ id (PK)    │
│  │ (FK)         │  │ (FK)         │  │ security_id  │  │ news_article│
│  │ last_price   │  │ period       │  │ (FK)         │  │ _id (FK)   │
│  │ bid_price    │  │ open_time    │  │ weight       │  │ security_id│
│  │ ask_price    │  │ open, high   │  │ shares_held  │  │ (FK)       │
│  │ volume       │  │ low, close   │  │ effective_date│ │ relevance  │
│  │ previous_close│ │ volume       │  │ end_date     │  │_score      │
│  │ timestamp    │  │ created_at   │  └──────────────┘  └────────────┘
│  │ (PARTITIONED)│  │ (PARTITIONED)│                                   │
│  └──────────────┘  └──────────────┘                                   │
│                                                                         │
│  ┌──────────────────────┐         ┌──────────────────────┐             │
│  │  indicator_values    │         │   indices            │             │
│  ├──────────────────────┤         ├──────────────────────┤             │
│  │ id (PK)              │         │ id (PK)              │             │
│  │ security_id (FK)─────┼────────►│ symbol (UNIQUE)      │             │
│  │ indicator_id (FK)    │         │ name                 │             │
│  │ period               │         │ index_type           │             │
│  │ value_time           │         │ base_value/date      │             │
│  │ value                │         └──────────────────────┘             │
│  │ extra_data (JSONB)   │              │                              │
│  └──────────────────────┘              │                              │
│                                     1:N │                              │
│                                        ▼                              │
│                                 ┌──────────────────┐                  │
│                                 │  index_quotes    │                  │
│                                 ├──────────────────┤                  │
│                                 │ id (PK)          │                  │
│                                 │ index_id (FK)    │                  │
│                                 │ value            │                  │
│                                 │ change_points    │                  │
│                                 │ timestamp        │                  │
│                                 └──────────────────┘                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      USER & ACCOUNT MANAGEMENT                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐                                              │
│  │      users           │◄──────────1:N──────────┐                    │
│  ├──────────────────────┤                        │                    │
│  │ id (PK, UUID)        │                    ┌────────────────────┐   │
│  │ email (UNIQUE)       │                    │  user_profiles     │   │
│  │ username (UNIQUE)    │                    ├────────────────────┤   │
│  │ password_hash        │                    │ id (PK, UUID)      │   │
│  │ account_type         │                    │ user_id (FK, UQ)   │   │
│  │ status               │                    │ theme              │   │
│  │ email_verified       │                    │ language           │   │
│  │ risk_tolerance       │                    │ currency           │   │
│  │ account_value        │                    │ notification_prefs │   │
│  │ cash_balance         │                    │ avatar_url         │   │
│  │ created_at           │                    └────────────────────┘   │
│  │ last_login_at        │                                              │
│  └──────────────────────┘                                              │
│         │                                                               │
│         │                                                               │
│     1:N │                                                               │
│   ┌─────┴──────┬──────────────┬──────────────┬──────────────┐         │
│   │            │              │              │              │         │
│   ▼            ▼              ▼              ▼              ▼         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │
│ │positions │ │  orders  │ │watchlists│ │ sessions  │ │price_    │  │
│ │          │ │          │ │          │ │           │ │alerts    │  │
│ ├──────────┤ ├──────────┤ ├──────────┤ ├───────────┤ ├──────────┤  │
│ │ id (PK)  │ │ id (PK)  │ │ id (PK)  │ │ id (PK)   │ │ id (PK)  │  │
│ │ user_id  │ │ user_id  │ │ user_id  │ │ user_id   │ │ user_id  │  │
│ │ security │ │ security │ │ name     │ │ token_hash│ │ security │  │
│ │_id (FK)  │ │_id (FK)  │ │ is_      │ │ expires_at│ │_id (FK)  │  │
│ │ quantity │ │ side     │ │default   │ │ ip_addr   │ │ alert_   │  │
│ │ avg_cost │ │ qty      │ │ order_   │ │ user_agent│ │type      │  │
│ │_price    │ │ price    │ │index     │ │ created_at│ │ trigger_ │  │
│ │ cost_    │ │ status   │ │ created_ │ │ revoked_at│ │price     │  │
│ │basis     │ │ filled   │ │at        │ │           │ │ is_active│  │
│ │ market_  │ │_qty      │ └──────────┘ └───────────┘ │ triggered│  │
│ │value     │ │ commission         1:N   │ at        │  │
│ │ unrealized│ │ created_at         │     │ notified_ │  │
│ │_gain_loss│ │ updated_at         │     │ at        │  │
│ │ dividend │ └──────────┘         ▼     └──────────┘  │
│ │_income   │      │            ┌──────────────────┐   │
│ │ 1st_purch│      │            │watchlist_items   │   │
│ │_date     │      │            ├──────────────────┤   │
│ └──────────┘      │            │ id (PK)          │   │
│       │           │            │ watchlist_id(FK) │   │
│       │        1:N │            │ security_id(FK)  │   │
│       │           │            │ added_at         │   │
│       │           │            │ order_index      │   │
│       │           ▼            │ notes            │   │
│       │    ┌──────────────────┐└──────────────────┘   │
│       │    │order_executions  │                       │
│       │    ├──────────────────┤                       │
│       │    │ id (PK)          │                       │
│       │    │ order_id (FK)    │                       │
│       │    │ executed_qty     │                       │
│       │    │ executed_price   │                       │
│       │    │ execution_ts     │                       │
│       │    │ execution_venue  │                       │
│       │    └──────────────────┘                       │
│       │                                                │
│       │ 1:N                                            │
│       ▼                                                │
│  ┌──────────────────┐                                 │
│  │  transactions    │                                 │
│  │  (PARTITIONED)   │                                 │
│  ├──────────────────┤                                 │
│  │ id (PK, UUID)    │                                 │
│  │ user_id (FK)     │                                 │
│  │ security_id (FK) │                                 │
│  │ type             │                                 │
│  │ quantity         │                                 │
│  │ price            │                                 │
│  │ amount           │                                 │
│  │ commission       │                                 │
│  │ trans_date       │                                 │
│  │ settled_date     │                                 │
│  │ created_at       │                                 │
│  └──────────────────┘                                 │
│                                                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                   PORTFOLIO VALUATION & ANALYTICS                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐                                              │
│  │portfolio_valuations  │                                              │
│  ├──────────────────────┤                                              │
│  │ id (PK, UUID)        │                                              │
│  │ user_id (FK)         │                                              │
│  │ total_cost_basis     │                                              │
│  │ total_market_value   │                                              │
│  │ total_unrealized_gl  │                                              │
│  │ cash_balance         │                                              │
│  │ total_account_value  │                                              │
│  │ snapshot_date        │                                              │
│  │ created_at           │                                              │
│  └──────────────────────┘                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    NEWS, EARNINGS & SEC FILINGS                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐      ┌──────────────────────┐               │
│  │  news_articles       │      │ earnings_calendar    │               │
│  ├──────────────────────┤      ├──────────────────────┤               │
│  │ id (PK, UUID)        │      │ id (PK, UUID)        │               │
│  │ headline             │      │ security_id (FK)     │               │
│  │ summary              │      │ earnings_date        │               │
│  │ content              │      │ eps_estimate/actual  │               │
│  │ source               │      │ revenue_estimate     │               │
│  │ sentiment_score      │      │ fiscal_period_end    │               │
│  │ sentiment_label      │      │ time_of_day          │               │
│  │ published_at         │      │ created_at           │               │
│  └──────────────────────┘      └──────────────────────┘               │
│           │                                                            │
│           │ 1:N                                                        │
│           │                      ┌──────────────────────┐             │
│           └─────────────────────►│  sec_filings         │             │
│                                  ├──────────────────────┤             │
│                                  │ id (PK, UUID)        │             │
│                                  │ security_id (FK)     │             │
│                                  │ filing_type          │             │
│                                  │ filing_date          │             │
│                                  │ period_end_date      │             │
│                                  │ sec_url              │             │
│                                  │ filing_summary       │             │
│                                  │ created_at           │             │
│                                  └──────────────────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                   SCREENERS & ALERTS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐                                              │
│  │     screeners        │◄─────────1:N──────────┐                     │
│  ├──────────────────────┤                       │                     │
│  │ id (PK, UUID)        │                   ┌────────────────────┐    │
│  │ user_id (FK)         │                   │screening_results   │    │
│  │ name                 │                   ├────────────────────┤    │
│  │ description          │                   │ id (PK, UUID)      │    │
│  │ criteria (JSONB)     │                   │ screener_id (FK)   │    │
│  │ is_public            │                   │ security_id (FK)   │    │
│  │ created_at           │                   │ matched_at         │    │
│  │ updated_at           │                   │ created_at         │    │
│  └──────────────────────┘                   └────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                   AUDIT & COMPLIANCE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────┐      ┌──────────────────────┐            │
│  │   audit_logs             │      │transaction_audit_    │            │
│  │ (PARTITIONED)            │      │trail                 │            │
│  ├──────────────────────────┤      ├──────────────────────┤            │
│  │ id (PK, UUID)            │      │ id (PK, UUID)        │            │
│  │ user_id (FK)             │      │ transaction_id (FK)  │            │
│  │ entity_type              │      │ status               │            │
│  │ entity_id                │      │ status_reason        │            │
│  │ action                   │      │ changed_by (FK)      │            │
│  │ old_values (JSONB)       │      │ created_at           │            │
│  │ new_values (JSONB)       │      └──────────────────────┘            │
│  │ ip_address               │                                          │
│  │ user_agent               │                                          │
│  │ created_at               │                                          │
│  └──────────────────────────┘                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Key Design Decisions

### 3.1 Partitioning Strategy

**OHLC Data (ohlc_data_partitioned)**
- Partitioned by DATE_TRUNC('day', open_time)
- Monthly partition children for easier management
- Retention: 3 years active, archive older
- Expected: 500GB/month at scale

**Quotes (quotes_partitioned)**
- Partitioned by DATE_TRUNC('day', timestamp)
- Daily partitions for high-frequency tick data
- Retention: 1 month in detail, aggregate to OHLC
- Expected: 50GB/day at scale

**Transactions (transactions_partitioned)**
- Partitioned by DATE_TRUNC('year', transaction_date)
- Annual partitions for long-term compliance retention
- No archival (regulatory requirement)
- Expected: 50GB/year

**Audit Logs (audit_logs_partitioned)**
- Partitioned by DATE_TRUNC('month', created_at)
- Monthly partitions for compliance
- Retention: 2 years
- Expected: 10GB/month

### 3.2 Indexing Strategy

**Hot Path Queries:**
```sql
-- Portfolio summary by user
idx_positions_user_id
idx_positions_user_id_security_id

-- Quote updates (high throughput)
idx_quotes_security_id_timestamp
idx_quotes_timestamp

-- OHLC retrieval for charts
idx_ohlc_data_security_period_time
idx_ohlc_data_open_time

-- User transactions
idx_transactions_user_id_transaction_date
idx_orders_user_id_status

-- Market data lookups
idx_securities_symbol
idx_securities_sector
idx_security_fundamentals_security_id
```

### 3.3 Data Types & Constraints

**DECIMAL for financial data:**
- Price: DECIMAL(12, 4) - supports up to $999,999.9999
- Amounts: DECIMAL(18, 2) - supports up to $999,999,999,999.99
- Percentages: DECIMAL(8, 4) - supports -9999.9999 to 9999.9999
- Ratios: DECIMAL(8, 6) - for index weights and small calculations

**UUID for user-facing IDs:**
- Cannot be guessed or enumerated
- Distributed across shards if needed
- Better privacy than sequential integers

**BIGINT for high-volume counts:**
- volume: BIGINT (can exceed 2.1B shares/day)
- shares_outstanding: BIGINT
- audit log IDs: BIGSERIAL

**JSONB for flexible schema:**
- Screener criteria (can evolve)
- Indicator parameters (supports different types)
- Audit trail changes (tracks any field changes)

### 3.4 Foreign Key Constraints

All foreign keys use ON DELETE CASCADE to:
- Maintain referential integrity
- Clean up related data when parent deleted
- Example: Deleting a security cascades to all quotes, positions, transactions

Notable exception:
- audit_logs.user_id: ON DELETE SET NULL (preserve audit trail even if user deleted)

---

## 4. Performance Optimization Queries

### 4.1 Portfolio Calculation (<100ms target)
```sql
SELECT
    SUM(CASE WHEN quantity > 0 THEN market_value ELSE 0 END) as total_market_value,
    SUM(CASE WHEN quantity > 0 THEN unrealized_gain_loss ELSE 0 END) as gains,
    cash_balance,
    (SUM(CASE WHEN quantity > 0 THEN market_value ELSE 0 END) + cash_balance) as total_value
FROM positions p
JOIN users u ON u.id = p.user_id
WHERE u.id = $1 AND quantity > 0;
```

**Optimization:**
- Materialized view (mv_portfolio_summary) with 5-minute refresh
- Index on (user_id, quantity)
- Fast aggregate function pre-calculation

### 4.2 Quote Updates (1000s per second)
```sql
INSERT INTO quotes (security_id, last_price, bid_price, ask_price, volume, timestamp)
VALUES ($1, $2, $3, $4, $5, $6);
```

**Optimization:**
- Partitioning by timestamp eliminates old data from scans
- Batch inserts in application layer
- No foreign key checks on security_id (denormalized)

### 4.3 Chart Data Retrieval (<500ms target)
```sql
SELECT open_time, open, high, low, close, volume
FROM ohlc_data
WHERE security_id = $1 AND period = $2
  AND open_time BETWEEN $3 AND $4
ORDER BY open_time;
```

**Optimization:**
- Unique index on (security_id, period, open_time)
- Partition elimination on date range
- Pre-computed OHLC (not derived from quotes)

### 4.4 Screener Execution (<2s for complex criteria)
```sql
-- Screener result view with lazy evaluation
SELECT s.id, s.symbol, s.name, m.current_price
FROM securities s
JOIN mv_security_performance m ON s.id = m.id
WHERE m.sector = $1
  AND m.price_to_earnings < $2
  AND m.dividend_yield > $3
  AND m.market_cap > $4;
```

**Optimization:**
- Materialized view pre-filters to active securities
- Index on sector and fundamentals
- JSONB filtering in application (complex logic)

---

## 5. Scalability Architecture

### 5.1 Read Scalability
- Materialized views for common queries
- Replication to read-only replicas
- Connection pooling for concurrent users

### 5.2 Write Scalability
- Partitioning reduces lock contention
- Batch quote inserts
- Async processing for analytics

### 5.3 Storage Scalability
- Partitioning enables archival
- Data retention policies
- Column compression for historical data

---

## 6. Backup & Recovery

### 6.1 Recovery Point Objectives (RPO)
- Database: 1 hour (point-in-time recovery)
- Transaction logs: Continuous archiving
- Audit logs: Immutable (append-only)

### 6.2 Backup Strategy
```bash
# Full backup weekly
pg_basebackup -D /backups/$(date +%Y%m%d) -Ft -z -P

# WAL archiving (continuous)
archive_command = 'test ! -f /wal_archive/%f && cp %p /wal_archive/%f'

# Restore point-in-time
pg_restore -d stockexchange -t orders /backups/2024_01_01
```

### 6.3 High Availability
- Primary database with synchronous replication
- Standby replica with auto-failover
- Load balancer for read/write distribution

---

## 7. Migration Strategy

### Phase 1: MVP (Months 1-2)
- Core tables only (securities, quotes, users, positions, orders)
- No partitioning initially (< 1GB data)
- Basic indexes

### Phase 2: Early Scale (Months 3-4)
- Add watchlists, watchlist alerts, screeners
- Implement OHLC data aggregation
- Add partitioning to quotes

### Phase 3: Advanced Features (Months 5-6)
- News and sentiment analysis
- Technical indicators
- SEC filings tracking
- Partition OHLC and transactions

### Phase 4: Optimization (Months 7+)
- Materialized view implementation
- Performance tuning
- Archive old data
- Implement pg_cron scheduling

---

## 8. Database Constraints & Validation

### 8.1 Business Logic Constraints
```sql
-- Unique constraints
UNIQUE(users.email)
UNIQUE(securities.symbol)
UNIQUE(watchlist_items.watchlist_id, security_id)
UNIQUE(positions.user_id, security_id) WHERE quantity > 0

-- Check constraints needed:
ALTER TABLE quotes ADD CHECK (ask_price >= bid_price);
ALTER TABLE positions ADD CHECK (quantity >= 0);
ALTER TABLE orders ADD CHECK (quantity > 0);
ALTER TABLE orders ADD CHECK (price IS NOT NULL OR order_type = 'market');
```

### 8.2 Data Integrity
- Foreign key cascades for referential integrity
- NOT NULL constraints on critical fields
- Default values for timestamps and status fields
- Audit logging on all modifications

---

## 9. Query Examples

### 9.1 Real-time Portfolio Summary
```sql
SELECT * FROM v_user_portfolio_summary WHERE user_id = $1;
```

### 9.2 Position Details with Current Prices
```sql
SELECT * FROM v_user_positions_detailed WHERE user_id = $1;
```

### 9.3 Active Orders with Status
```sql
SELECT * FROM v_user_orders_status WHERE user_id = $1;
```

### 9.4 Market Data with Performance
```sql
SELECT * FROM v_security_market_data WHERE symbol = $1;
```

### 9.5 Watchlist Performance
```sql
SELECT * FROM v_watchlist_performance WHERE watchlist_id = $1;
```

---

## 10. Compliance & Regulatory

### 10.1 Audit Trail
- All transactions logged with user_id, timestamp, IP
- Immutable audit_logs with 2-year retention
- Transaction audit trail tracks order-to-execution

### 10.2 KYC/AML Fields
- User account type (retail/professional/institutional)
- Risk tolerance tracking
- Account status (pending_verification, active, suspended, closed)

### 10.3 Data Retention
- Quotes: 1 month detailed, aggregate to OHLC
- OHLC: 3 years active
- Transactions: Indefinite
- Audit logs: 2 years
- Sessions: Auto-delete expired after 24 hours

---

## 11. Future Extensions (Phase 3+)

### Options Data
```sql
CREATE TABLE options_contracts (
    id SERIAL PRIMARY KEY,
    underlying_security_id INTEGER REFERENCES securities(id),
    contract_symbol VARCHAR(50) UNIQUE,
    option_type VARCHAR(4), -- call, put
    strike_price DECIMAL(12, 4),
    expiration_date DATE,
    ...
);
```

### Cryptocurrency Integration
```sql
-- Reuse securities table with asset_class = 'crypto'
-- Add blockchain-specific fields:
ALTER TABLE securities ADD COLUMN blockchain_id VARCHAR(100);
ALTER TABLE securities ADD COLUMN smart_contract_address VARCHAR(255);
```

### Advanced Analytics
```sql
CREATE TABLE technical_analysis_cache (
    security_id INTEGER,
    period VARCHAR(10),
    calculated_at TIMESTAMP,
    rsi DECIMAL(8, 4),
    macd_line DECIMAL(12, 4),
    signal_line DECIMAL(12, 4),
    bollinger_upper DECIMAL(12, 4),
    bollinger_middle DECIMAL(12, 4),
    bollinger_lower DECIMAL(12, 4),
    UNIQUE(security_id, period, calculated_at)
);
```

---

## 12. Index Summary

| Table | Index | Purpose | Est. Size |
|-------|-------|---------|-----------|
| securities | idx_securities_symbol | Symbol lookup | 50MB |
| securities | idx_securities_sector | Sector filtering | 50MB |
| quotes | idx_quotes_security_id_timestamp | Quote retrieval | 2GB |
| ohlc_data | idx_ohlc_data_security_period_time | Chart data | 500MB |
| positions | idx_positions_user_id | Portfolio queries | 100MB |
| orders | idx_orders_user_id_status | Order retrieval | 200MB |
| transactions | idx_transactions_user_id_transaction_date | History queries | 300MB |
| audit_logs | idx_audit_logs_user_id | Compliance | 500MB |
| **Total** | | | ~4GB |

