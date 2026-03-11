-- ============================================================================
-- Stock Exchange Board Application - Views and Optimized Queries
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- 1. PORTFOLIO & POSITION VIEWS
-- ============================================================================

-- Get current portfolio summary for a user
CREATE OR REPLACE VIEW v_user_portfolio_summary AS
SELECT
    u.id as user_id,
    u.email,
    u.username,
    COUNT(DISTINCT p.security_id) as holdings_count,
    COUNT(DISTINCT o.id) as open_orders_count,
    SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END) as total_cost_basis,
    SUM(CASE WHEN p.quantity > 0 THEN p.market_value ELSE 0 END) as total_market_value,
    SUM(CASE WHEN p.quantity > 0 THEN p.unrealized_gain_loss ELSE 0 END) as total_unrealized_gain_loss,
    u.cash_balance,
    (SUM(CASE WHEN p.quantity > 0 THEN p.market_value ELSE 0 END) + u.cash_balance) as total_account_value,
    CASE
        WHEN (SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END)) > 0
        THEN ((SUM(CASE WHEN p.quantity > 0 THEN p.market_value ELSE 0 END) + u.cash_balance - SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END))
            / SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END) * 100)
        ELSE 0
    END as total_return_percent,
    CASE
        WHEN (SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END)) > 0
        THEN ((SUM(CASE WHEN p.quantity > 0 THEN p.market_value ELSE 0 END) - SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END))
            / SUM(CASE WHEN p.quantity > 0 THEN p.cost_basis ELSE 0 END) * 100)
        ELSE 0
    END as unrealized_gain_loss_percent
FROM users u
LEFT JOIN positions p ON u.id = p.user_id
LEFT JOIN orders o ON u.id = o.user_id AND o.status NOT IN ('filled', 'cancelled', 'rejected')
GROUP BY u.id, u.email, u.username, u.cash_balance;

-- Get detailed position information with current pricing
CREATE OR REPLACE VIEW v_user_positions_detailed AS
SELECT
    p.id as position_id,
    p.user_id,
    s.id as security_id,
    s.symbol,
    s.name,
    s.sector,
    s.industry,
    p.quantity,
    p.average_cost_price,
    p.cost_basis,
    q.last_price as current_price,
    p.market_value,
    p.unrealized_gain_loss,
    p.unrealized_gain_loss_percent,
    p.dividend_income,
    sf.dividend_yield,
    sf.price_to_earnings,
    sf.fifty_two_week_high,
    fifty_two_week_low,
    ((q.last_price - sf.fifty_two_week_low) / (sf.fifty_two_week_high - sf.fifty_two_week_low) * 100)::DECIMAL(8,2) as position_in_52w_range,
    p.first_purchased_at,
    q.timestamp as last_quote_time
FROM positions p
INNER JOIN securities s ON p.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        timestamp
    FROM quotes
    WHERE security_id IS NOT NULL
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id
WHERE p.quantity > 0;

-- ============================================================================
-- 2. WATCHLIST VIEWS
-- ============================================================================

-- Watchlist with performance metrics
CREATE OR REPLACE VIEW v_watchlist_performance AS
SELECT
    w.id as watchlist_id,
    w.user_id,
    w.name as watchlist_name,
    wi.id as item_id,
    s.id as security_id,
    s.symbol,
    s.name as security_name,
    q.last_price,
    q.bid_price,
    q.ask_price,
    q.volume,
    sf.fifty_two_week_high,
    sf.fifty_two_week_low,
    ((q.last_price - q.previous_close) / q.previous_close * 100) as daily_change_percent,
    ((q.last_price - sf.fifty_two_week_low) / (sf.fifty_two_week_high - sf.fifty_two_week_low) * 100) as fifty_two_week_position,
    wi.added_at,
    w.order_index
FROM watchlists w
INNER JOIN watchlist_items wi ON w.id = wi.watchlist_id
INNER JOIN securities s ON wi.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        bid_price,
        ask_price,
        volume,
        previous_close,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id;

-- ============================================================================
-- 3. ORDER & EXECUTION VIEWS
-- ============================================================================

-- Active and recent orders with fill information
CREATE OR REPLACE VIEW v_user_orders_status AS
SELECT
    o.id as order_id,
    o.user_id,
    s.symbol,
    s.name,
    o.order_type,
    o.side,
    o.quantity,
    o.price,
    o.stop_price,
    o.status,
    o.filled_quantity,
    (o.filled_quantity / NULLIF(o.quantity, 0) * 100)::DECIMAL(8,2) as fill_percentage,
    o.average_fill_price,
    COALESCE(o.total_cost, 0) as total_cost,
    o.commission,
    o.time_in_force,
    o.good_until_date,
    o.created_at,
    o.updated_at,
    CASE
        WHEN o.status = 'pending' THEN 'Awaiting execution'
        WHEN o.status = 'partial_filled' THEN concat(o.filled_quantity::TEXT, ' / ', o.quantity::TEXT, ' filled')
        WHEN o.status = 'filled' THEN 'Completed'
        WHEN o.status = 'cancelled' THEN 'Cancelled'
        WHEN o.status = 'rejected' THEN o.rejection_reason
        ELSE o.status
    END as status_description,
    -- Calculate days until expiration for GTC orders
    CASE
        WHEN o.time_in_force = 'gtc' AND o.expires_at IS NOT NULL
        THEN (o.expires_at::DATE - CURRENT_DATE)
        ELSE NULL
    END as days_until_expiry
FROM orders o
INNER JOIN securities s ON o.security_id = s.id
WHERE o.status IN ('pending', 'partial_filled', 'filled', 'cancelled', 'rejected')
ORDER BY o.created_at DESC;

-- Order execution details with fills
CREATE OR REPLACE VIEW v_order_execution_details AS
SELECT
    o.id as order_id,
    o.user_id,
    s.symbol,
    o.side,
    o.order_type,
    o.quantity as total_quantity,
    SUM(oe.executed_quantity) as total_executed,
    COUNT(oe.id) as execution_count,
    MIN(oe.execution_timestamp) as first_execution_time,
    MAX(oe.execution_timestamp) as last_execution_time,
    AVG(oe.executed_price) as average_execution_price,
    STRING_AGG(
        CONCAT(oe.executed_quantity::TEXT, ' @ $', oe.executed_price::TEXT, ' (', TO_CHAR(oe.execution_timestamp, 'HH24:MI:SS'), ')'),
        ', ' ORDER BY oe.execution_timestamp
    ) as execution_details
FROM orders o
INNER JOIN securities s ON o.security_id = s.id
LEFT JOIN order_executions oe ON o.id = oe.order_id
GROUP BY o.id, o.user_id, s.symbol, o.side, o.order_type, o.quantity;

-- ============================================================================
-- 4. MARKET DATA VIEWS
-- ============================================================================

-- Security performance with technical indicators
CREATE OR REPLACE VIEW v_security_market_data AS
SELECT
    s.id as security_id,
    s.symbol,
    s.name,
    e.code as exchange,
    s.sector,
    s.industry,
    q.last_price,
    q.open,
    q.high,
    q.low,
    q.bid_price,
    q.ask_price,
    q.volume,
    ((q.last_price - q.previous_close) / q.previous_close * 100)::DECIMAL(8,4) as daily_change_percent,
    (q.last_price - q.previous_close)::DECIMAL(12,4) as daily_change_amount,
    sf.fifty_two_week_high,
    sf.fifty_two_week_low,
    sf.fifty_two_week_high - sf.fifty_two_week_low as fifty_two_week_range,
    ((q.last_price - sf.fifty_two_week_low) / (sf.fifty_two_week_high - sf.fifty_two_week_low) * 100)::DECIMAL(8,2) as fifty_two_week_position,
    sf.market_cap,
    sf.earnings_per_share,
    sf.price_to_earnings,
    sf.dividend_yield,
    sf.avg_volume_50d,
    sf.avg_volume_200d,
    q.timestamp as last_quote_time,
    s.status
FROM securities s
LEFT JOIN exchanges e ON s.exchange_id = e.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        open,
        high,
        low,
        bid_price,
        ask_price,
        volume,
        previous_close,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id
WHERE s.status = 'active';

-- Sector performance aggregation
CREATE OR REPLACE VIEW v_sector_performance AS
SELECT
    s.sector,
    COUNT(DISTINCT s.id) as stock_count,
    AVG(q.last_price) as avg_price,
    SUM(q.volume) as total_volume,
    SUM(sf.market_cap) as sector_market_cap,
    AVG((q.last_price - q.previous_close) / q.previous_close * 100)::DECIMAL(8,4) as avg_daily_change_percent,
    MIN(q.last_price) as lowest_price,
    MAX(q.last_price) as highest_price,
    MAX(q.timestamp) as last_update
FROM securities s
LEFT JOIN quotes q ON s.id = q.security_id AND q.timestamp = (
    SELECT MAX(timestamp) FROM quotes q2 WHERE q2.security_id = s.id
)
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id
WHERE s.status = 'active' AND s.sector IS NOT NULL
GROUP BY s.sector
ORDER BY sector_market_cap DESC NULLS LAST;

-- ============================================================================
-- 5. PRICE ALERT VIEWS
-- ============================================================================

-- Active price alerts with current prices
CREATE OR REPLACE VIEW v_active_price_alerts AS
SELECT
    pa.id as alert_id,
    pa.user_id,
    s.symbol,
    s.name,
    pa.alert_type,
    pa.trigger_price,
    pa.trigger_percent_change,
    q.last_price,
    CASE
        WHEN pa.alert_type = 'above'
        THEN CASE
            WHEN q.last_price >= pa.trigger_price THEN 'TRIGGERED'
            ELSE 'PENDING'
        END
        WHEN pa.alert_type = 'below'
        THEN CASE
            WHEN q.last_price <= pa.trigger_price THEN 'TRIGGERED'
            ELSE 'PENDING'
        END
        WHEN pa.alert_type = 'change_percent'
        THEN CASE
            WHEN ABS((q.last_price - q.previous_close) / q.previous_close * 100) >= ABS(pa.trigger_percent_change)
            THEN 'TRIGGERED'
            ELSE 'PENDING'
        END
        ELSE 'UNKNOWN'
    END as alert_status,
    (q.last_price - pa.trigger_price)::DECIMAL(12,4) as difference_from_trigger,
    pa.created_at,
    pa.triggered_at,
    pa.notified_at
FROM price_alerts pa
INNER JOIN users u ON pa.user_id = u.id
INNER JOIN securities s ON pa.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        previous_close,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
WHERE pa.is_active = true;

-- ============================================================================
-- 6. NEWS & EARNINGS VIEWS
-- ============================================================================

-- Recent news with associated securities
CREATE OR REPLACE VIEW v_news_with_securities AS
SELECT
    na.id as news_id,
    na.headline,
    na.summary,
    na.source,
    na.sentiment_score,
    na.sentiment_label,
    na.published_at,
    STRING_AGG(s.symbol, ', ') as related_symbols,
    STRING_AGG(s.id::TEXT, ',') as security_ids,
    COUNT(DISTINCT nsa.security_id) as security_count
FROM news_articles na
LEFT JOIN news_security_association nsa ON na.id = nsa.news_article_id
LEFT JOIN securities s ON nsa.security_id = s.id
GROUP BY na.id, na.headline, na.summary, na.source, na.sentiment_score, na.sentiment_label, na.published_at
ORDER BY na.published_at DESC;

-- Upcoming earnings
CREATE OR REPLACE VIEW v_upcoming_earnings AS
SELECT
    ec.id as earnings_id,
    s.symbol,
    s.name,
    ec.earnings_date,
    ec.earnings_date_confidence,
    ec.fiscal_period_end,
    ec.eps_estimate,
    ec.eps_actual,
    CASE
        WHEN ec.eps_actual IS NOT NULL AND ec.eps_estimate IS NOT NULL
        THEN ((ec.eps_actual - ec.eps_estimate) / ABS(ec.eps_estimate) * 100)::DECIMAL(8,4)
        ELSE NULL
    END as eps_surprise_percent,
    ec.revenue_estimate,
    ec.revenue_actual,
    ec.time_of_day,
    (ec.earnings_date - CURRENT_DATE) as days_until_earnings,
    q.last_price,
    q.bid_price,
    q.ask_price,
    q.volume
FROM earnings_calendar ec
INNER JOIN securities s ON ec.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        bid_price,
        ask_price,
        volume,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
WHERE ec.earnings_date >= CURRENT_DATE
ORDER BY ec.earnings_date ASC;

-- ============================================================================
-- 7. SCREENER RESULT VIEWS
-- ============================================================================

-- Latest screening results with prices
CREATE OR REPLACE VIEW v_screener_results_latest AS
SELECT
    sr.screener_id,
    sc.name as screener_name,
    sc.user_id,
    COUNT(DISTINCT sr.security_id) as matching_stocks,
    MAX(sr.matched_at) as last_screening_time,
    JSON_BUILD_OBJECT(
        'total_matches', COUNT(DISTINCT sr.security_id),
        'latest_run', MAX(sr.matched_at)::TEXT
    ) as screening_stats
FROM screening_results sr
INNER JOIN screeners sc ON sr.screener_id = sc.id
GROUP BY sr.screener_id, sc.name, sc.user_id
ORDER BY MAX(sr.matched_at) DESC;

-- Screening results with market data
CREATE OR REPLACE VIEW v_screener_results_with_data AS
SELECT
    sr.screener_id,
    sc.name as screener_name,
    sr.security_id,
    s.symbol,
    s.name as security_name,
    s.sector,
    q.last_price,
    q.bid_price,
    q.ask_price,
    q.volume,
    ((q.last_price - q.previous_close) / q.previous_close * 100)::DECIMAL(8,4) as daily_change_percent,
    sf.market_cap,
    sf.price_to_earnings,
    sf.dividend_yield,
    sr.matched_at as screening_time
FROM screening_results sr
INNER JOIN screeners sc ON sr.screener_id = sc.id
INNER JOIN securities s ON sr.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        bid_price,
        ask_price,
        volume,
        previous_close,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id
ORDER BY sr.screener_id, sr.matched_at DESC, s.symbol;

-- ============================================================================
-- 8. INDEX & BENCHMARK VIEWS
-- ============================================================================

-- Index performance tracking
CREATE OR REPLACE VIEW v_index_performance AS
SELECT
    i.id as index_id,
    i.symbol,
    i.name,
    i.index_type,
    iq.value as current_value,
    iq.change_points,
    iq.change_percent,
    (
        SELECT COUNT(*)
        FROM index_constituents ic
        WHERE ic.index_id = i.id
        AND (ic.end_date IS NULL OR ic.end_date >= CURRENT_DATE)
    ) as constituent_count,
    iq.timestamp as last_update
FROM indices i
LEFT JOIN (
    SELECT DISTINCT ON (index_id)
        index_id,
        value,
        change_points,
        change_percent,
        timestamp
    FROM index_quotes
    ORDER BY index_id, timestamp DESC
) iq ON i.id = iq.index_id
ORDER BY i.symbol;

-- Index constituents with weights and performance
CREATE OR REPLACE VIEW v_index_constituents_detailed AS
SELECT
    ic.index_id,
    i.symbol as index_symbol,
    ic.security_id,
    s.symbol,
    s.name,
    ic.weight,
    ic.weight * 100 as weight_percent,
    ic.shares_held,
    q.last_price,
    ((q.last_price - q.previous_close) / q.previous_close * 100)::DECIMAL(8,4) as daily_change_percent,
    (ic.weight * ((q.last_price - q.previous_close) / q.previous_close * 100))::DECIMAL(8,6) as contribution_to_index_change
FROM index_constituents ic
INNER JOIN indices i ON ic.index_id = i.id
INNER JOIN securities s ON ic.security_id = s.id
LEFT JOIN (
    SELECT DISTINCT ON (security_id)
        security_id,
        last_price,
        previous_close,
        timestamp
    FROM quotes
    ORDER BY security_id, timestamp DESC
) q ON s.id = q.security_id
WHERE ic.end_date IS NULL OR ic.end_date >= CURRENT_DATE
ORDER BY ic.index_id, ic.weight DESC;

-- ============================================================================
-- 9. PERFORMANCE & ANALYTICS VIEWS
-- ============================================================================

-- User trading activity summary
CREATE OR REPLACE VIEW v_user_trading_activity AS
SELECT
    t.user_id,
    u.email,
    u.username,
    DATE_TRUNC('month', t.transaction_date)::DATE as month,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN t.transaction_type = 'buy' THEN 1 ELSE 0 END) as buy_count,
    SUM(CASE WHEN t.transaction_type = 'sell' THEN 1 ELSE 0 END) as sell_count,
    SUM(ABS(t.amount)) as total_volume,
    SUM(CASE WHEN t.transaction_type = 'buy' THEN t.amount ELSE 0 END) as buy_volume,
    SUM(CASE WHEN t.transaction_type = 'sell' THEN t.amount ELSE 0 END) as sell_volume,
    SUM(t.commission) as total_commission,
    COUNT(DISTINCT t.security_id) as unique_securities_traded
FROM transactions t
INNER JOIN users u ON t.user_id = u.id
GROUP BY t.user_id, u.email, u.username, DATE_TRUNC('month', t.transaction_date);

-- Dividend income tracking
CREATE OR REPLACE VIEW v_dividend_income_summary AS
SELECT
    p.user_id,
    u.email,
    DATE_TRUNC('year', t.transaction_date)::DATE as year,
    SUM(CASE WHEN t.transaction_type = 'dividend' THEN t.amount ELSE 0 END) as total_dividend_income,
    COUNT(DISTINCT CASE WHEN t.transaction_type = 'dividend' THEN t.security_id END) as dividend_paying_stocks,
    STRING_AGG(DISTINCT s.symbol, ', ') FILTER (WHERE t.transaction_type = 'dividend') as dividend_stocks
FROM positions p
INNER JOIN users u ON p.user_id = u.id
LEFT JOIN transactions t ON p.user_id = t.user_id
LEFT JOIN securities s ON t.security_id = s.id
WHERE t.transaction_type = 'dividend'
GROUP BY p.user_id, u.email, DATE_TRUNC('year', t.transaction_date);

-- ============================================================================
-- 10. COMPLIANCE & AUDIT VIEWS
-- ============================================================================

-- Login activity
CREATE OR REPLACE VIEW v_user_login_activity AS
SELECT
    u.id as user_id,
    u.email,
    u.username,
    COUNT(DISTINCT a.id) as total_logins,
    MAX(a.created_at) as last_login,
    COUNT(DISTINCT DATE(a.created_at)) as login_days,
    STRING_AGG(DISTINCT a.ip_address::TEXT, ', ') as used_ip_addresses
FROM users u
LEFT JOIN audit_logs a ON u.id = a.user_id AND a.action = 'login'
GROUP BY u.id, u.email, u.username
ORDER BY MAX(a.created_at) DESC NULLS LAST;

-- Suspicious activity detection
CREATE OR REPLACE VIEW v_suspicious_activity AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(*) as activity_count,
    COUNT(DISTINCT a.ip_address) as unique_ips,
    STRING_AGG(DISTINCT a.action, ', ') as actions,
    STRING_AGG(DISTINCT a.ip_address::TEXT, ', ') as ip_addresses,
    MIN(a.created_at) as first_activity,
    MAX(a.created_at) as last_activity
FROM users u
INNER JOIN audit_logs a ON u.id = a.user_id
WHERE DATE(a.created_at) = CURRENT_DATE
GROUP BY u.id, u.email
HAVING COUNT(DISTINCT a.ip_address) > 5 OR COUNT(*) > 100
ORDER BY COUNT(*) DESC;

-- ============================================================================
-- MATERIALIZED VIEW REFRESH PROCEDURES
-- ============================================================================

CREATE OR REPLACE PROCEDURE refresh_materialized_views()
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_portfolio_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_security_performance;
    RAISE NOTICE 'Materialized views refreshed at %', NOW();
END;
$$;

-- Schedule this to run periodically (e.g., every 5 minutes during market hours)
-- SELECT cron.schedule('refresh-mvs', '*/5 * 9-16 * * 1-5', 'CALL refresh_materialized_views();');
