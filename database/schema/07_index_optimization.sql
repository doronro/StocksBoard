-- ============================================================================
-- Stock Exchange Board - Index Optimization & Additional Performance Indexes
-- Run these after initial deployment when query patterns are identified
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- PORTFOLIO OPTIMIZATION INDEXES
-- ============================================================================

-- Speed up portfolio queries by user
CREATE INDEX IF NOT EXISTS idx_positions_user_quantity
ON positions(user_id, quantity DESC)
WHERE quantity > 0;

-- Speed up finding current holdings
CREATE INDEX IF NOT EXISTS idx_positions_user_security_quantity
ON positions(user_id, security_id, quantity DESC);

-- Portfolio valuations by user and date range
CREATE INDEX IF NOT EXISTS idx_portfolio_valuations_user_date
ON portfolio_valuations(user_id, snapshot_date DESC);

-- ============================================================================
-- ORDER MANAGEMENT OPTIMIZATION
-- ============================================================================

-- Active orders for a user
CREATE INDEX IF NOT EXISTS idx_orders_user_status_created
ON orders(user_id, status, created_at DESC)
WHERE status IN ('pending', 'partial_filled');

-- Orders by security for market data
CREATE INDEX IF NOT EXISTS idx_orders_security_status_created
ON orders(security_id, status, created_at DESC);

-- Time-based order cleanup
CREATE INDEX IF NOT EXISTS idx_orders_expires_at
ON orders(expires_at)
WHERE status = 'pending' AND time_in_force = 'gtc';

-- Order execution search
CREATE INDEX IF NOT EXISTS idx_order_executions_order_timestamp
ON order_executions(order_id, execution_timestamp DESC);

-- ============================================================================
-- TRANSACTION HISTORY OPTIMIZATION
-- ============================================================================

-- User transaction history lookup (partitioned, but local index speeds up)
CREATE INDEX IF NOT EXISTS idx_transactions_user_security_date
ON transactions(user_id, security_id, transaction_date DESC)
WHERE transaction_type IN ('buy', 'sell');

-- Find all dividends for a user
CREATE INDEX IF NOT EXISTS idx_transactions_user_dividend
ON transactions(user_id, transaction_date DESC)
WHERE transaction_type = 'dividend';

-- ============================================================================
-- WATCHLIST OPTIMIZATION
-- ============================================================================

-- User's default watchlist lookup
CREATE INDEX IF NOT EXISTS idx_watchlists_user_default
ON watchlists(user_id)
WHERE is_default = true;

-- Watchlist item performance (important for real-time display)
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_order
ON watchlist_items(watchlist_id, order_index ASC);

-- ============================================================================
-- QUOTE & MARKET DATA OPTIMIZATION
-- ============================================================================

-- Latest quote for each security (important query pattern)
CREATE INDEX IF NOT EXISTS idx_quotes_security_timestamp_desc
ON quotes(security_id, timestamp DESC);

-- Range queries for quote history
CREATE INDEX IF NOT EXISTS idx_quotes_timestamp_security
ON quotes(timestamp DESC, security_id);

-- Volume analysis queries
CREATE INDEX IF NOT EXISTS idx_quotes_security_volume
ON quotes(security_id, volume DESC);

-- ============================================================================
-- OHLC DATA OPTIMIZATION
-- ============================================================================

-- Multi-period queries (find data for multiple timeframes at once)
CREATE INDEX IF NOT EXISTS idx_ohlc_data_security_open_time
ON ohlc_data(security_id, open_time DESC);

-- Period-specific queries
CREATE INDEX IF NOT EXISTS idx_ohlc_data_period_time
ON ohlc_data(period, open_time DESC);

-- Range queries for charting (year/month/day filtering)
CREATE INDEX IF NOT EXISTS idx_ohlc_data_open_time_date
ON ohlc_data(DATE(open_time), open_time DESC);

-- ============================================================================
-- SECURITY & FUNDAMENTALS OPTIMIZATION
-- ============================================================================

-- Sector and industry filtering (for screeners)
CREATE INDEX IF NOT EXISTS idx_securities_sector_industry_status
ON securities(sector, industry, status)
WHERE status = 'active';

-- Find ETFs vs stocks
CREATE INDEX IF NOT EXISTS idx_securities_is_etf_status
ON securities(is_etf, status)
WHERE status = 'active';

-- Asset class filtering
CREATE INDEX IF NOT EXISTS idx_securities_asset_class_status
ON securities(asset_class, status)
WHERE status = 'active';

-- Fundamental metric filtering (for screeners)
CREATE INDEX IF NOT EXISTS idx_security_fundamentals_metrics
ON security_fundamentals(
    price_to_earnings,
    dividend_yield,
    market_cap
);

-- ============================================================================
-- INDEX CONSTITUENT OPTIMIZATION
-- ============================================================================

-- Find all securities in an index
CREATE INDEX IF NOT EXISTS idx_index_constituents_index_effective
ON index_constituents(index_id, effective_date DESC)
WHERE end_date IS NULL OR end_date >= CURRENT_DATE;

-- Find which indices contain a security
CREATE INDEX IF NOT EXISTS idx_index_constituents_security_effective
ON index_constituents(security_id, effective_date DESC)
WHERE end_date IS NULL OR end_date >= CURRENT_DATE;

-- Weight-based queries
CREATE INDEX IF NOT EXISTS idx_index_constituents_weight
ON index_constituents(index_id, weight DESC);

-- ============================================================================
-- TECHNICAL INDICATOR OPTIMIZATION
-- ============================================================================

-- Latest indicator value for a security
CREATE INDEX IF NOT EXISTS idx_indicator_values_latest
ON indicator_values(security_id, indicator_id, period, value_time DESC);

-- Indicator screening (find values meeting criteria)
CREATE INDEX IF NOT EXISTS idx_indicator_values_metric
ON indicator_values(indicator_id, period, value, value_time DESC);

-- ============================================================================
-- NEWS & SENTIMENT OPTIMIZATION
-- ============================================================================

-- Recent news queries
CREATE INDEX IF NOT EXISTS idx_news_articles_published_sentiment
ON news_articles(published_at DESC, sentiment_score DESC);

-- Sentiment filtering
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment_label
ON news_articles(sentiment_label, published_at DESC)
WHERE sentiment_label IS NOT NULL;

-- News-security association (for related stories)
CREATE INDEX IF NOT EXISTS idx_news_security_association_security_published
ON news_security_association(security_id)
WHERE news_article_id IN (
    SELECT id FROM news_articles
    WHERE published_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
);

-- ============================================================================
-- EARNINGS & SEC FILINGS OPTIMIZATION
-- ============================================================================

-- Upcoming earnings
CREATE INDEX IF NOT EXISTS idx_earnings_calendar_upcoming
ON earnings_calendar(security_id, earnings_date)
WHERE earnings_date >= CURRENT_DATE;

-- Earnings surprise analysis
CREATE INDEX IF NOT EXISTS idx_earnings_calendar_eps_surprise
ON earnings_calendar(eps_actual - eps_estimate DESC)
WHERE eps_actual IS NOT NULL AND eps_estimate IS NOT NULL;

-- SEC filings by type
CREATE INDEX IF NOT EXISTS idx_sec_filings_type_date
ON sec_filings(security_id, filing_type, filing_date DESC);

-- ============================================================================
-- SCREENER OPTIMIZATION
-- ============================================================================

-- User's screeners
CREATE INDEX IF NOT EXISTS idx_screeners_user_updated
ON screeners(user_id, updated_at DESC);

-- Latest screening results for a screener
CREATE INDEX IF NOT EXISTS idx_screening_results_screener_date
ON screening_results(screener_id, matched_at DESC);

-- Find users monitoring a security
CREATE INDEX IF NOT EXISTS idx_screening_results_security_screener
ON screening_results(security_id, screener_id);

-- ============================================================================
-- PRICE ALERT OPTIMIZATION
-- ============================================================================

-- Active alerts for a user
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_active
ON price_alerts(user_id, is_active)
WHERE is_active = true;

-- Find triggered but not notified alerts
CREATE INDEX IF NOT EXISTS idx_price_alerts_triggered_unnotified
ON price_alerts(triggered_at, notified_at)
WHERE triggered_at IS NOT NULL AND notified_at IS NULL;

-- Security monitoring (find who's watching this stock)
CREATE INDEX IF NOT EXISTS idx_price_alerts_security_user
ON price_alerts(security_id, user_id, is_active)
WHERE is_active = true;

-- ============================================================================
-- AUDIT & COMPLIANCE OPTIMIZATION
-- ============================================================================

-- User activity audit (partitioned, but local helps)
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_entity_action
ON audit_logs(user_id, entity_type, action, created_at DESC);

-- Entity change tracking
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type_date
ON audit_logs(entity_type, created_at DESC);

-- Suspicious activity detection
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_ip_address
ON audit_logs(action, ip_address, created_at DESC)
WHERE action IN ('login', 'unauthorized_access');

-- Transaction compliance audit
CREATE INDEX IF NOT EXISTS idx_transaction_audit_trail_status
ON transaction_audit_trail(transaction_id, status, created_at DESC);

-- ============================================================================
-- SESSION & AUTHENTICATION OPTIMIZATION
-- ============================================================================

-- Fast session lookup
CREATE INDEX IF NOT EXISTS idx_sessions_user_id_not_revoked
ON sessions(user_id)
WHERE revoked_at IS NULL;

-- Token validation lookup
CREATE INDEX IF NOT EXISTS idx_sessions_token_hash_expires
ON sessions(token_hash, expires_at)
WHERE revoked_at IS NULL;

-- Cleanup expired sessions
CREATE INDEX IF NOT EXISTS idx_sessions_cleanup
ON sessions(expires_at)
WHERE expires_at < CURRENT_TIMESTAMP;

-- ============================================================================
-- USER MANAGEMENT OPTIMIZATION
-- ============================================================================

-- Account status filtering
CREATE INDEX IF NOT EXISTS idx_users_status_created
ON users(status, created_at DESC);

-- Account type filtering (for KYC/AML)
CREATE INDEX IF NOT EXISTS idx_users_account_type_status
ON users(account_type, status);

-- Last login analysis
CREATE INDEX IF NOT EXISTS idx_users_last_login
ON users(last_login_at DESC)
WHERE last_login_at IS NOT NULL;

-- ============================================================================
-- PARTIAL INDEXES (For specific use cases)
-- ============================================================================

-- Active users only (more selective)
CREATE INDEX IF NOT EXISTS idx_users_active
ON users(id)
WHERE status = 'active';

-- Unverified emails (for notification campaigns)
CREATE INDEX IF NOT EXISTS idx_users_unverified_email
ON users(id, email)
WHERE email_verified = false;

-- Users with 2FA enabled
CREATE INDEX IF NOT EXISTS idx_users_2fa_enabled
ON users(id)
WHERE two_factor_enabled = true;

-- ============================================================================
-- EXPRESSION INDEXES (For specific queries)
-- ============================================================================

-- Fast portfolio return calculation
CREATE INDEX IF NOT EXISTS idx_positions_return_percent
ON positions((
    CASE
        WHEN quantity > 0 THEN unrealized_gain_loss_percent
        ELSE NULL
    END DESC
))
WHERE quantity > 0;

-- Case-insensitive security lookup
CREATE INDEX IF NOT EXISTS idx_securities_symbol_lower
ON securities(LOWER(symbol))
WHERE status = 'active';

-- Date-based quote ranges
CREATE INDEX IF NOT EXISTS idx_quotes_date_range
ON quotes(security_id, DATE(timestamp))
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '1 month';

-- ============================================================================
-- INDEX MAINTENANCE & ANALYSIS
-- ============================================================================

-- Function to analyze index usage
CREATE OR REPLACE FUNCTION analyze_index_usage()
RETURNS TABLE(
    schema_name VARCHAR,
    table_name VARCHAR,
    index_name VARCHAR,
    size_mb DECIMAL,
    scan_count BIGINT,
    tup_read BIGINT,
    tup_fetch BIGINT,
    usage_ratio DECIMAL
) AS $$
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid))::DECIMAL,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE
        WHEN idx_tup_read > 0 THEN (idx_tup_fetch::DECIMAL / idx_tup_read * 100)::DECIMAL(8,2)
        ELSE NULL
    END as usage_ratio
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
$$ LANGUAGE SQL;

-- Function to find unused indexes
CREATE OR REPLACE FUNCTION find_unused_indexes()
RETURNS TABLE(
    schema_name VARCHAR,
    table_name VARCHAR,
    index_name VARCHAR,
    size_mb DECIMAL,
    scan_count BIGINT
) AS $$
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid))::DECIMAL,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexname NOT LIKE 'pg_toast%'
    AND pg_relation_size(indexrelid) > 1000000  -- > 1MB
ORDER BY pg_relation_size(indexrelid) DESC;
$$ LANGUAGE SQL;

-- Function to find missing indexes
CREATE OR REPLACE FUNCTION find_missing_indexes()
RETURNS TABLE(
    schema_name VARCHAR,
    table_name VARCHAR,
    column_names VARCHAR,
    index_recommendation VARCHAR
) AS $$
SELECT
    schemaname,
    tablename,
    attname,
    'CREATE INDEX idx_' || tablename || '_' || attname ||
    ' ON ' || schemaname || '.' || tablename || '(' || attname || ');'
FROM (
    SELECT
        t.schemaname,
        t.tablename,
        a.attname,
        ROW_NUMBER() OVER (PARTITION BY t.tablename, a.attname ORDER BY n_distinct DESC) as rn
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    JOIN pg_attribute a ON a.attrelid = c.oid
    JOIN pg_stats s ON s.tablename = t.tablename AND s.attname = a.attname
    WHERE t.schemaname = 'public'
        AND a.attnum > 0
        AND NOT a.attisdropped
        AND n_distinct > 100  -- Column has high cardinality
) sub
WHERE rn = 1
ORDER BY n_distinct DESC;
$$ LANGUAGE SQL;

-- ============================================================================
-- INDEX STATISTICS REFRESH
-- ============================================================================

-- Procedure to refresh all index statistics
CREATE OR REPLACE PROCEDURE refresh_index_statistics()
LANGUAGE plpgsql
AS $$
BEGIN
    ANALYZE;
    RAISE NOTICE 'Index statistics refreshed at %', NOW();
END;
$$;

-- ============================================================================
-- VALIDATION SCRIPT
-- ============================================================================

-- Run this after creating all indexes to verify coverage
SELECT
    'Total Indexes Created' as metric,
    COUNT(*)::TEXT as value
FROM pg_indexes
WHERE schemaname = 'public';

SELECT
    'Indexes by Table' as metric,
    tablename || ': ' || COUNT(*)::TEXT as value
FROM pg_indexes
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY COUNT(*) DESC;

SELECT
    'Total Index Size' as metric,
    pg_size_pretty(SUM(pg_relation_size(indexrelid)))::TEXT as value
FROM pg_stat_user_indexes;

-- ============================================================================
-- NOTES
-- ============================================================================

/*
INDEX CREATION STRATEGY:

1. Phase 1 (MVP): Only core indexes from 01_core_tables.sql
2. Phase 2: Add hot-path indexes after 1 month of usage
3. Phase 3: Add optimization indexes based on query patterns
4. Ongoing: Use analyze_index_usage() and find_unused_indexes() quarterly

BEST PRACTICES:

- Always include WHERE clauses in partial indexes
- Use expression indexes for computed values
- Monitor index size growth (should be < 25% of table size)
- Drop unused indexes (idx_scan = 0 for 30+ days)
- Refresh statistics after large inserts (ANALYZE)
- Use REINDEX for fragmented indexes

PERFORMANCE IMPACT:

- Indexes speed up SELECT queries
- Indexes slow down INSERT/UPDATE/DELETE
- Balance read/write patterns for your use case
- Monitor pg_stat_user_indexes for effectiveness

MAINTENANCE:

- REINDEX during off-hours for active tables
- ANALYZE after bulk loads
- CLUSTER to optimize physical order (rare, blocking)
- Drop duplicate indexes

Example Cron Jobs:
SELECT cron.schedule('weekly-reindex', '0 2 SUN * *', 'REINDEX;');
SELECT cron.schedule('index-stats', '0 */4 * * *', 'ANALYZE;');
*/
