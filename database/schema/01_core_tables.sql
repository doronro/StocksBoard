-- ============================================================================
-- Stock Exchange Board Application - PostgreSQL Schema
-- Core Tables Definition
-- Version: 1.0.0
-- Created: 2026-03-10
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. CORE REFERENCE TABLES
-- ============================================================================

-- Market/Exchange definitions
CREATE TABLE IF NOT EXISTS exchanges (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    timezone VARCHAR(50),
    opening_time TIME,
    closing_time TIME,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exchanges_code ON exchanges(code);

-- ============================================================================
-- 2. SECURITY/STOCK DATA TABLES
-- ============================================================================

-- Master stock/security data
CREATE TABLE IF NOT EXISTS securities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    isin VARCHAR(20) UNIQUE,
    cusip VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    exchange_id INTEGER REFERENCES exchanges(id),
    asset_class VARCHAR(50) NOT NULL, -- stock, etf, mutual_fund, crypto
    sector VARCHAR(100),
    industry VARCHAR(100),
    country_code VARCHAR(2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'active', -- active, delisted, suspended, merged
    listing_date DATE,
    delisting_date DATE,
    is_etf BOOLEAN DEFAULT false,
    description TEXT,
    website VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_securities_symbol ON securities(symbol);
CREATE INDEX idx_securities_exchange_id ON securities(exchange_id);
CREATE INDEX idx_securities_sector ON securities(sector);
CREATE INDEX idx_securities_asset_class ON securities(asset_class);
CREATE INDEX idx_securities_status ON securities(status);

-- Stock fundamentals and metrics
CREATE TABLE IF NOT EXISTS security_fundamentals (
    id SERIAL PRIMARY KEY,
    security_id INTEGER NOT NULL UNIQUE REFERENCES securities(id) ON DELETE CASCADE,
    market_cap BIGINT,
    shares_outstanding BIGINT,
    earnings_per_share DECIMAL(12, 4),
    price_to_earnings DECIMAL(12, 4),
    price_to_book DECIMAL(12, 4),
    dividend_yield DECIMAL(8, 4),
    annual_dividend DECIMAL(12, 4),
    fifty_two_week_high DECIMAL(12, 4),
    fifty_two_week_low DECIMAL(12, 4),
    avg_volume_50d BIGINT,
    avg_volume_200d BIGINT,
    beta DECIMAL(8, 4),
    debt_to_equity DECIMAL(8, 4),
    current_ratio DECIMAL(8, 4),
    roe DECIMAL(8, 4),
    revenue_ttm BIGINT,
    net_income_ttm BIGINT,
    free_cash_flow_ttm BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_security_fundamentals_security_id ON security_fundamentals(security_id);

-- Current/real-time quote data
CREATE TABLE IF NOT EXISTS quotes (
    id BIGSERIAL PRIMARY KEY,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotes_security_id_timestamp ON quotes(security_id, timestamp DESC);
CREATE INDEX idx_quotes_timestamp ON quotes(timestamp DESC);

-- OHLC candlestick data for charting
CREATE TABLE IF NOT EXISTS ohlc_data (
    id BIGSERIAL PRIMARY KEY,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    period VARCHAR(10) NOT NULL, -- 1m, 5m, 15m, 1h, 1d, 1w, 1mo
    open_time TIMESTAMP NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_ohlc_data_unique ON ohlc_data(security_id, period, open_time);
CREATE INDEX idx_ohlc_data_security_period_time ON ohlc_data(security_id, period, open_time DESC);
CREATE INDEX idx_ohlc_data_open_time ON ohlc_data(open_time DESC);

-- ============================================================================
-- 3. MARKET INDICES
-- ============================================================================

CREATE TABLE IF NOT EXISTS indices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    index_type VARCHAR(50), -- broad_market, sector, international, etc.
    country VARCHAR(100),
    base_value DECIMAL(12, 4),
    base_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_indices_symbol ON indices(symbol);

-- Index constituents
CREATE TABLE IF NOT EXISTS index_constituents (
    id SERIAL PRIMARY KEY,
    index_id INTEGER NOT NULL REFERENCES indices(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    weight DECIMAL(8, 6), -- weight in the index as a decimal (0.05 = 5%)
    shares_held BIGINT,
    effective_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_index_constituents_index_id ON index_constituents(index_id);
CREATE INDEX idx_index_constituents_security_id ON index_constituents(security_id);
CREATE INDEX idx_index_constituents_effective_date ON index_constituents(effective_date DESC);

-- Index historical data
CREATE TABLE IF NOT EXISTS index_quotes (
    id BIGSERIAL PRIMARY KEY,
    index_id INTEGER NOT NULL REFERENCES indices(id) ON DELETE CASCADE,
    value DECIMAL(12, 4) NOT NULL,
    change_points DECIMAL(12, 4),
    change_percent DECIMAL(8, 4),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_index_quotes_index_id_timestamp ON index_quotes(index_id, timestamp DESC);

-- ============================================================================
-- 4. USER & ACCOUNT MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) DEFAULT 'retail', -- retail, professional, institutional
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, closed, pending_verification
    email_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    phone_number VARCHAR(20),
    country_code VARCHAR(2),
    risk_tolerance VARCHAR(50), -- conservative, moderate, aggressive
    account_value DECIMAL(18, 2) DEFAULT 0,
    cash_balance DECIMAL(18, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- User profiles and preferences
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(50) DEFAULT 'light', -- light, dark, auto
    language VARCHAR(10) DEFAULT 'en',
    currency VARCHAR(3) DEFAULT 'USD',
    notifications_email BOOLEAN DEFAULT true,
    notifications_push BOOLEAN DEFAULT true,
    notifications_sms BOOLEAN DEFAULT false,
    broker_commission DECIMAL(8, 4) DEFAULT 0,
    default_order_type VARCHAR(20) DEFAULT 'market', -- market, limit, stop
    hide_balance BOOLEAN DEFAULT false,
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- Session/authentication tokens
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- ============================================================================
-- 5. WATCHLIST MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_watchlists_user_id_name ON watchlists(user_id, name);
CREATE UNIQUE INDEX idx_watchlists_user_default ON watchlists(user_id) WHERE is_default = true;

-- Watchlist items
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_index INTEGER,
    notes TEXT
);

CREATE INDEX idx_watchlist_items_watchlist_id ON watchlist_items(watchlist_id);
CREATE INDEX idx_watchlist_items_security_id ON watchlist_items(security_id);
CREATE UNIQUE INDEX idx_watchlist_items_unique ON watchlist_items(watchlist_id, security_id);

-- ============================================================================
-- 6. PORTFOLIO & HOLDINGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    quantity DECIMAL(18, 8) NOT NULL,
    average_cost_price DECIMAL(12, 4) NOT NULL,
    current_price DECIMAL(12, 4),
    cost_basis DECIMAL(18, 2) NOT NULL, -- quantity * average_cost_price
    market_value DECIMAL(18, 2), -- quantity * current_price
    unrealized_gain_loss DECIMAL(18, 2),
    unrealized_gain_loss_percent DECIMAL(8, 4),
    dividend_income DECIMAL(18, 2) DEFAULT 0,
    first_purchased_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_user_id ON positions(user_id);
CREATE INDEX idx_positions_security_id ON positions(security_id);
CREATE INDEX idx_positions_user_id_security_id ON positions(user_id, security_id);
CREATE UNIQUE INDEX idx_positions_unique ON positions(user_id, security_id) WHERE quantity > 0;

-- Portfolio valuation snapshots for tracking P&L
CREATE TABLE IF NOT EXISTS portfolio_valuations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_cost_basis DECIMAL(18, 2) NOT NULL,
    total_market_value DECIMAL(18, 2) NOT NULL,
    total_unrealized_gain_loss DECIMAL(18, 2),
    cash_balance DECIMAL(18, 2) NOT NULL,
    total_account_value DECIMAL(18, 2) NOT NULL,
    unrealized_gain_loss_percent DECIMAL(8, 4),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_portfolio_valuations_user_id ON portfolio_valuations(user_id);
CREATE INDEX idx_portfolio_valuations_user_snapshot_date ON portfolio_valuations(user_id, snapshot_date DESC);
CREATE UNIQUE INDEX idx_portfolio_valuations_unique ON portfolio_valuations(user_id, snapshot_date);

-- Transaction history (buys, sells, dividends, splits, etc.)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL, -- buy, sell, dividend, stock_split, spin_off, merger
    quantity DECIMAL(18, 8),
    price DECIMAL(12, 4),
    amount DECIMAL(18, 2) NOT NULL,
    commission DECIMAL(12, 4) DEFAULT 0,
    notes TEXT,
    external_transaction_id VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    settled_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_security_id ON transactions(security_id);
CREATE INDEX idx_transactions_user_id_transaction_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_transaction_type ON transactions(transaction_type);

-- ============================================================================
-- 7. ORDER MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    order_type VARCHAR(50) NOT NULL, -- market, limit, stop, stop_limit
    side VARCHAR(10) NOT NULL, -- buy, sell
    quantity DECIMAL(18, 8) NOT NULL,
    price DECIMAL(12, 4),
    stop_price DECIMAL(12, 4),
    status VARCHAR(50) DEFAULT 'pending', -- pending, filled, partial_filled, cancelled, rejected, expired
    filled_quantity DECIMAL(18, 8) DEFAULT 0,
    average_fill_price DECIMAL(12, 4),
    total_cost DECIMAL(18, 2),
    commission DECIMAL(12, 4),
    time_in_force VARCHAR(20) DEFAULT 'day', -- day, gtc, ioc, fok, opg
    good_until_date DATE,
    external_order_id VARCHAR(100),
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_security_id ON orders(security_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_user_id_status ON orders(user_id, status);

-- Order execution records
CREATE TABLE IF NOT EXISTS order_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    executed_quantity DECIMAL(18, 8) NOT NULL,
    executed_price DECIMAL(12, 4) NOT NULL,
    execution_timestamp TIMESTAMP NOT NULL,
    execution_venue VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_executions_order_id ON order_executions(order_id);
CREATE INDEX idx_order_executions_execution_timestamp ON order_executions(execution_timestamp DESC);

-- ============================================================================
-- 8. TECHNICAL INDICATORS & ANALYSIS
-- ============================================================================

CREATE TABLE IF NOT EXISTS indicators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    calculation_method TEXT,
    parameters JSONB, -- flexible parameters for different indicator types
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calculated indicator values
CREATE TABLE IF NOT EXISTS indicator_values (
    id BIGSERIAL PRIMARY KEY,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    indicator_id INTEGER NOT NULL REFERENCES indicators(id),
    period VARCHAR(10), -- 1m, 5m, 15m, 1h, 1d, 1w, 1mo
    value_time TIMESTAMP NOT NULL,
    value DECIMAL(18, 6),
    extra_data JSONB, -- for multi-value indicators like Bollinger Bands, MACD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_indicator_values_security_indicator ON indicator_values(security_id, indicator_id, period);
CREATE INDEX idx_indicator_values_value_time ON indicator_values(value_time DESC);

-- ============================================================================
-- 9. NEWS & SENTIMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    headline VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    source VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000),
    author VARCHAR(255),
    sentiment_score DECIMAL(5, 3), -- -1.0 to 1.0
    sentiment_label VARCHAR(20), -- negative, neutral, positive
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_articles_published_at ON news_articles(published_at DESC);
CREATE INDEX idx_news_articles_sentiment_score ON news_articles(sentiment_score);

-- Association between news and securities
CREATE TABLE IF NOT EXISTS news_security_association (
    id SERIAL PRIMARY KEY,
    news_article_id UUID NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    relevance_score DECIMAL(5, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_security_association_security_id ON news_security_association(security_id);
CREATE INDEX idx_news_security_association_news_article_id ON news_security_association(news_article_id);
CREATE UNIQUE INDEX idx_news_security_association_unique ON news_security_association(news_article_id, security_id);

-- Earnings calendar
CREATE TABLE IF NOT EXISTS earnings_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    earnings_date DATE NOT NULL,
    earnings_date_confidence VARCHAR(50), -- confirmed, expected, unconfirmed
    fiscal_period_end DATE,
    eps_estimate DECIMAL(12, 4),
    eps_actual DECIMAL(12, 4),
    revenue_estimate BIGINT,
    revenue_actual BIGINT,
    time_of_day VARCHAR(20), -- pre_market, after_hours, closed_market
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_earnings_calendar_security_id ON earnings_calendar(security_id);
CREATE INDEX idx_earnings_calendar_earnings_date ON earnings_calendar(earnings_date);

-- SEC filings tracker
CREATE TABLE IF NOT EXISTS sec_filings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    filing_type VARCHAR(20) NOT NULL, -- 10-K, 10-Q, 8-K, S-1, etc.
    filing_date DATE NOT NULL,
    period_end_date DATE,
    sec_url VARCHAR(1000),
    filing_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sec_filings_security_id ON sec_filings(security_id);
CREATE INDEX idx_sec_filings_filing_type ON sec_filings(filing_type);
CREATE INDEX idx_sec_filings_filing_date ON sec_filings(filing_date DESC);

-- ============================================================================
-- 10. SCREENERS & ALERTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS screeners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    criteria JSONB NOT NULL, -- flexible criteria structure
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_screeners_user_id ON screeners(user_id);

-- Screening results with timestamps
CREATE TABLE IF NOT EXISTS screening_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    screener_id UUID NOT NULL REFERENCES screeners(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    matched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_screening_results_screener_id ON screening_results(screener_id);
CREATE INDEX idx_screening_results_security_id ON screening_results(security_id);
CREATE UNIQUE INDEX idx_screening_results_unique ON screening_results(screener_id, security_id, matched_at::DATE);

-- Price alerts and notifications
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL, -- above, below, change_percent
    trigger_price DECIMAL(12, 4),
    trigger_percent_change DECIMAL(8, 4),
    is_active BOOLEAN DEFAULT true,
    triggered_at TIMESTAMP,
    notified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_security_id ON price_alerts(security_id);
CREATE INDEX idx_price_alerts_is_active ON price_alerts(is_active);

-- ============================================================================
-- 11. AUDIT & COMPLIANCE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    action VARCHAR(50) NOT NULL, -- create, update, delete, login, logout
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Transaction audit trail for compliance
CREATE TABLE IF NOT EXISTS transaction_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    status_reason TEXT,
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_audit_trail_transaction_id ON transaction_audit_trail(transaction_id);
CREATE INDEX idx_transaction_audit_trail_status ON transaction_audit_trail(status);

-- ============================================================================
-- 12. DATA RETENTION & ARCHIVAL
-- ============================================================================

CREATE TABLE IF NOT EXISTS archived_ohlc_data (
    LIKE ohlc_data INCLUDING ALL
);

CREATE TABLE IF NOT EXISTS archived_quotes (
    LIKE quotes INCLUDING ALL
);

-- Partitioning metadata for time-series data
CREATE TABLE IF NOT EXISTS partition_metadata (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    partition_key VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50), -- active, archived, deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 13. SYSTEM METADATA & CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50), -- string, integer, boolean, json
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sync/cache status
CREATE TABLE IF NOT EXISTS data_sync_status (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(100) NOT NULL, -- quotes, ohlc, fundamentals, indices
    security_id INTEGER REFERENCES securities(id),
    last_sync_time TIMESTAMP,
    next_sync_time TIMESTAMP,
    sync_status VARCHAR(50), -- pending, in_progress, completed, failed
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_sync_status_data_type ON data_sync_status(data_type);
CREATE INDEX idx_data_sync_status_security_id ON data_sync_status(security_id);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_portfolio_summary AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(DISTINCT p.security_id) as holdings_count,
    SUM(p.cost_basis) as total_cost_basis,
    SUM(p.market_value) as total_market_value,
    SUM(p.unrealized_gain_loss) as total_unrealized_gain_loss,
    u.cash_balance,
    (SUM(p.market_value) + u.cash_balance) as total_account_value,
    CASE
        WHEN SUM(p.market_value) + u.cash_balance > 0
        THEN ((SUM(p.market_value) + u.cash_balance - SUM(p.cost_basis)) / (SUM(p.cost_basis)) * 100)
        ELSE 0
    END as total_return_percent
FROM users u
LEFT JOIN positions p ON u.id = p.user_id AND p.quantity > 0
GROUP BY u.id, u.email, u.cash_balance;

CREATE UNIQUE INDEX idx_mv_portfolio_summary_user_id ON mv_portfolio_summary(user_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_security_performance AS
SELECT
    s.id,
    s.symbol,
    s.name,
    q.last_price,
    sf.fifty_two_week_high,
    sf.fifty_two_week_low,
    ((q.last_price - q.previous_close) / q.previous_close * 100) as daily_change_percent,
    ((q.last_price - sf.fifty_two_week_low) / (sf.fifty_two_week_high - sf.fifty_two_week_low) * 100) as fifty_two_week_position,
    q.timestamp as last_quote_time,
    s.sector,
    s.industry
FROM securities s
LEFT JOIN quotes q ON s.id = q.security_id
    AND q.timestamp = (SELECT MAX(timestamp) FROM quotes q2 WHERE q2.security_id = s.id)
LEFT JOIN security_fundamentals sf ON s.id = sf.security_id
WHERE s.status = 'active';

CREATE UNIQUE INDEX idx_mv_security_performance_id ON mv_security_performance(id);
CREATE INDEX idx_mv_security_performance_sector ON mv_security_performance(sector);
