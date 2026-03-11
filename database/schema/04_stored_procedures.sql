-- ============================================================================
-- Stock Exchange Board Application - Stored Procedures
-- Core business logic and atomic operations
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- 1. ORDER MANAGEMENT PROCEDURES
-- ============================================================================

-- Execute a market order and update user positions
CREATE OR REPLACE FUNCTION execute_market_order(
    p_order_id UUID,
    p_executed_quantity DECIMAL,
    p_executed_price DECIMAL,
    p_execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    position_id UUID,
    new_quantity DECIMAL,
    new_average_cost DECIMAL
) AS $$
DECLARE
    v_order orders%ROWTYPE;
    v_user_id UUID;
    v_security_id INTEGER;
    v_side VARCHAR;
    v_position positions%ROWTYPE;
    v_total_cost DECIMAL;
    v_new_quantity DECIMAL;
    v_new_average_cost DECIMAL;
    v_user_cash_balance DECIMAL;
BEGIN
    -- Get order details
    SELECT * INTO v_order FROM orders WHERE id = p_order_id FOR UPDATE;

    IF v_order.id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Order not found'::TEXT, NULL::UUID, NULL::DECIMAL, NULL::DECIMAL;
        RETURN;
    END IF;

    v_user_id := v_order.user_id;
    v_security_id := v_order.security_id;
    v_side := v_order.side;

    -- Lock user account to prevent concurrent modifications
    SELECT cash_balance INTO v_user_cash_balance FROM users WHERE id = v_user_id FOR UPDATE;

    -- Calculate cost
    v_total_cost := p_executed_quantity * p_executed_price;

    -- Validate sufficient funds for buy orders
    IF v_side = 'buy' AND (v_user_cash_balance - v_total_cost) < 0 THEN
        RETURN QUERY SELECT FALSE, 'Insufficient funds'::TEXT, NULL::UUID, NULL::DECIMAL, NULL::DECIMAL;
        RETURN;
    END IF;

    -- Get or create position
    SELECT * INTO v_position FROM positions
    WHERE user_id = v_user_id AND security_id = v_security_id
    FOR UPDATE;

    IF v_side = 'buy' THEN
        IF v_position.id IS NULL THEN
            -- Create new position
            INSERT INTO positions (
                user_id, security_id, quantity, average_cost_price,
                cost_basis, current_price, market_value,
                unrealized_gain_loss, unrealized_gain_loss_percent,
                first_purchased_at, last_updated_at
            ) VALUES (
                v_user_id, v_security_id, p_executed_quantity, p_executed_price,
                v_total_cost, p_executed_price, v_total_cost,
                0, 0,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) RETURNING * INTO v_position;
        ELSE
            -- Update existing position - recalculate average cost
            v_new_quantity := v_position.quantity + p_executed_quantity;
            v_new_average_cost := (v_position.cost_basis + v_total_cost) / v_new_quantity;

            UPDATE positions SET
                quantity = v_new_quantity,
                average_cost_price = v_new_average_cost,
                cost_basis = v_new_quantity * v_new_average_cost,
                current_price = p_executed_price,
                market_value = v_new_quantity * p_executed_price,
                unrealized_gain_loss = (v_new_quantity * p_executed_price) - (v_new_quantity * v_new_average_cost),
                unrealized_gain_loss_percent = ((v_new_quantity * p_executed_price) - (v_new_quantity * v_new_average_cost)) / (v_new_quantity * v_new_average_cost) * 100,
                last_updated_at = CURRENT_TIMESTAMP
            WHERE user_id = v_user_id AND security_id = v_security_id
            RETURNING * INTO v_position;
        END IF;

        -- Deduct from cash balance
        UPDATE users SET
            cash_balance = cash_balance - v_total_cost,
            account_value = (SELECT SUM(market_value) FROM positions WHERE user_id = v_user_id AND quantity > 0)
                + (users.cash_balance - v_total_cost),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = v_user_id;

    ELSIF v_side = 'sell' THEN
        IF v_position.id IS NULL OR v_position.quantity < p_executed_quantity THEN
            RETURN QUERY SELECT FALSE, 'Insufficient position to sell'::TEXT, NULL::UUID, NULL::DECIMAL, NULL::DECIMAL;
            RETURN;
        END IF;

        -- Update position - reduce quantity
        v_new_quantity := v_position.quantity - p_executed_quantity;

        IF v_new_quantity = 0 THEN
            -- Close position
            DELETE FROM positions WHERE id = v_position.id;
        ELSE
            -- Partial sale - average cost stays the same
            UPDATE positions SET
                quantity = v_new_quantity,
                cost_basis = v_new_quantity * average_cost_price,
                current_price = p_executed_price,
                market_value = v_new_quantity * p_executed_price,
                unrealized_gain_loss = (v_new_quantity * p_executed_price) - (v_new_quantity * average_cost_price),
                unrealized_gain_loss_percent = ((v_new_quantity * p_executed_price) - (v_new_quantity * average_cost_price)) / (v_new_quantity * average_cost_price) * 100,
                last_updated_at = CURRENT_TIMESTAMP
            WHERE id = v_position.id
            RETURNING * INTO v_position;
        END IF;

        -- Add to cash balance
        UPDATE users SET
            cash_balance = cash_balance + v_total_cost,
            account_value = (SELECT SUM(market_value) FROM positions WHERE user_id = v_user_id AND quantity > 0)
                + (users.cash_balance + v_total_cost),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = v_user_id;
    END IF;

    -- Record execution
    INSERT INTO order_executions (order_id, executed_quantity, executed_price, execution_timestamp)
    VALUES (p_order_id, p_executed_quantity, p_executed_price, p_execution_timestamp);

    -- Update order
    UPDATE orders SET
        filled_quantity = filled_quantity + p_executed_quantity,
        average_fill_price = ((filled_quantity * COALESCE(average_fill_price, 0)) + v_total_cost) / (filled_quantity + p_executed_quantity),
        total_cost = ((filled_quantity * COALESCE(average_fill_price, 0)) + v_total_cost),
        status = CASE
            WHEN (filled_quantity + p_executed_quantity) >= quantity THEN 'filled'
            ELSE 'partial_filled'
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_order_id;

    -- Record transaction
    INSERT INTO transactions (
        user_id, security_id, transaction_type, quantity, price,
        amount, commission, transaction_date, settled_date
    ) VALUES (
        v_user_id, v_security_id, v_side, p_executed_quantity, p_executed_price,
        v_total_cost, 0, p_execution_timestamp, p_execution_timestamp
    );

    -- Record audit log
    INSERT INTO audit_logs (
        user_id, entity_type, entity_id, action, new_values
    ) VALUES (
        v_user_id, 'order', p_order_id::TEXT, 'execute',
        JSONB_BUILD_OBJECT(
            'quantity', p_executed_quantity,
            'price', p_executed_price,
            'timestamp', p_execution_timestamp
        )
    );

    RETURN QUERY SELECT
        TRUE,
        'Order executed successfully'::TEXT,
        v_position.id,
        v_position.quantity,
        v_position.average_cost_price;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 2. PORTFOLIO VALUATION PROCEDURES
-- ============================================================================

-- Calculate and record daily portfolio valuation
CREATE OR REPLACE FUNCTION calculate_portfolio_valuation(p_user_id UUID)
RETURNS TABLE(
    total_cost_basis DECIMAL,
    total_market_value DECIMAL,
    total_unrealized_gain_loss DECIMAL,
    unrealized_gain_loss_percent DECIMAL
) AS $$
DECLARE
    v_total_cost_basis DECIMAL := 0;
    v_total_market_value DECIMAL := 0;
    v_total_unrealized_gain_loss DECIMAL := 0;
    v_cash_balance DECIMAL;
    v_unrealized_percent DECIMAL := 0;
BEGIN
    -- Get cash balance
    SELECT cash_balance INTO v_cash_balance FROM users WHERE id = p_user_id;

    -- Calculate totals from positions
    SELECT
        COALESCE(SUM(cost_basis), 0),
        COALESCE(SUM(market_value), 0),
        COALESCE(SUM(unrealized_gain_loss), 0)
    INTO v_total_cost_basis, v_total_market_value, v_total_unrealized_gain_loss
    FROM positions
    WHERE user_id = p_user_id AND quantity > 0;

    -- Calculate percentage return
    IF v_total_cost_basis > 0 THEN
        v_unrealized_percent := (v_total_unrealized_gain_loss / v_total_cost_basis) * 100;
    END IF;

    -- Insert valuation snapshot
    INSERT INTO portfolio_valuations (
        user_id, total_cost_basis, total_market_value,
        total_unrealized_gain_loss, cash_balance,
        total_account_value, unrealized_gain_loss_percent,
        snapshot_date, created_at
    ) VALUES (
        p_user_id, v_total_cost_basis, v_total_market_value,
        v_total_unrealized_gain_loss, v_cash_balance,
        v_total_market_value + v_cash_balance, v_unrealized_percent,
        CURRENT_DATE, CURRENT_TIMESTAMP
    )
    ON CONFLICT (user_id, snapshot_date) DO UPDATE SET
        total_cost_basis = EXCLUDED.total_cost_basis,
        total_market_value = EXCLUDED.total_market_value,
        total_unrealized_gain_loss = EXCLUDED.total_unrealized_gain_loss,
        cash_balance = EXCLUDED.cash_balance,
        total_account_value = EXCLUDED.total_account_value,
        unrealized_gain_loss_percent = EXCLUDED.unrealized_gain_loss_percent,
        created_at = CURRENT_TIMESTAMP;

    RETURN QUERY SELECT
        v_total_cost_basis,
        v_total_market_value,
        v_total_unrealized_gain_loss,
        v_unrealized_percent;
END;
$$ LANGUAGE plpgsql;

-- Update all user portfolio valuations
CREATE OR REPLACE PROCEDURE calculate_all_portfolio_valuations()
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;
BEGIN
    FOR v_user_id IN SELECT id FROM users WHERE status = 'active' LOOP
        PERFORM calculate_portfolio_valuation(v_user_id);
    END LOOP;
    RAISE NOTICE 'Portfolio valuations calculated for all active users at %', NOW();
END;
$$;

-- ============================================================================
-- 3. WATCHLIST MANAGEMENT PROCEDURES
-- ============================================================================

-- Add security to watchlist
CREATE OR REPLACE FUNCTION add_to_watchlist(
    p_user_id UUID,
    p_symbol VARCHAR,
    p_watchlist_id UUID DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    watchlist_item_id UUID
) AS $$
DECLARE
    v_watchlist_id UUID;
    v_security_id INTEGER;
    v_item_id UUID;
BEGIN
    -- Get or create default watchlist
    IF p_watchlist_id IS NULL THEN
        SELECT id INTO v_watchlist_id FROM watchlists
        WHERE user_id = p_user_id AND is_default = true
        LIMIT 1;

        IF v_watchlist_id IS NULL THEN
            INSERT INTO watchlists (user_id, name, is_default)
            VALUES (p_user_id, 'My Watchlist', true)
            RETURNING id INTO v_watchlist_id;
        END IF;
    ELSE
        v_watchlist_id := p_watchlist_id;
    END IF;

    -- Get security ID
    SELECT id INTO v_security_id FROM securities WHERE symbol = p_symbol LIMIT 1;

    IF v_security_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Security not found'::TEXT, NULL::UUID;
        RETURN;
    END IF;

    -- Check if already in watchlist
    SELECT id INTO v_item_id FROM watchlist_items
    WHERE watchlist_id = v_watchlist_id AND security_id = v_security_id;

    IF v_item_id IS NOT NULL THEN
        RETURN QUERY SELECT FALSE, 'Already in watchlist'::TEXT, v_item_id;
        RETURN;
    END IF;

    -- Add to watchlist
    INSERT INTO watchlist_items (watchlist_id, security_id)
    VALUES (v_watchlist_id, v_security_id)
    RETURNING watchlist_items.id INTO v_item_id;

    RETURN QUERY SELECT TRUE, 'Added to watchlist'::TEXT, v_item_id;
END;
$$ LANGUAGE plpgsql;

-- Remove security from watchlist
CREATE OR REPLACE FUNCTION remove_from_watchlist(
    p_watchlist_item_id UUID
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
BEGIN
    DELETE FROM watchlist_items WHERE id = p_watchlist_item_id;

    IF FOUND THEN
        RETURN QUERY SELECT TRUE, 'Removed from watchlist'::TEXT;
    ELSE
        RETURN QUERY SELECT FALSE, 'Watchlist item not found'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. PRICE ALERT PROCEDURES
-- ============================================================================

-- Check and trigger price alerts
CREATE OR REPLACE FUNCTION check_price_alerts()
RETURNS TABLE(
    triggered_count INTEGER
) AS $$
DECLARE
    v_triggered_count INTEGER := 0;
    v_alert record;
    v_current_price DECIMAL;
BEGIN
    -- Find alerts that should be triggered
    FOR v_alert IN
        SELECT pa.id, pa.alert_type, pa.trigger_price, pa.trigger_percent_change,
               q.last_price, q.previous_close, s.symbol
        FROM price_alerts pa
        INNER JOIN securities s ON pa.security_id = s.id
        LEFT JOIN (
            SELECT DISTINCT ON (security_id) security_id, last_price, previous_close
            FROM quotes ORDER BY security_id, timestamp DESC
        ) q ON s.id = q.security_id
        WHERE pa.is_active = true AND pa.triggered_at IS NULL
    LOOP
        v_current_price := v_alert.last_price;

        -- Check if alert should trigger
        IF (v_alert.alert_type = 'above' AND v_current_price >= v_alert.trigger_price) OR
           (v_alert.alert_type = 'below' AND v_current_price <= v_alert.trigger_price) OR
           (v_alert.alert_type = 'change_percent' AND
            ABS((v_current_price - v_alert.previous_close) / v_alert.previous_close * 100) >= ABS(v_alert.trigger_percent_change))
        THEN
            -- Mark alert as triggered
            UPDATE price_alerts SET
                triggered_at = CURRENT_TIMESTAMP,
                notified_at = CURRENT_TIMESTAMP
            WHERE id = v_alert.id;

            v_triggered_count := v_triggered_count + 1;

            -- Log this trigger
            INSERT INTO audit_logs (
                entity_type, entity_id, action, new_values
            ) VALUES (
                'price_alert', v_alert.id::TEXT, 'triggered',
                JSONB_BUILD_OBJECT(
                    'symbol', v_alert.symbol,
                    'price', v_current_price,
                    'triggered_at', CURRENT_TIMESTAMP
                )
            );
        END IF;
    END LOOP;

    RETURN QUERY SELECT v_triggered_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. DIVIDEND & CORPORATE ACTION PROCEDURES
-- ============================================================================

-- Record dividend payment
CREATE OR REPLACE FUNCTION record_dividend_payment(
    p_security_id INTEGER,
    p_dividend_per_share DECIMAL,
    p_payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE(
    processed_positions INTEGER,
    total_dividend_amount DECIMAL
) AS $$
DECLARE
    v_processed_count INTEGER := 0;
    v_total_amount DECIMAL := 0;
    v_position_record record;
BEGIN
    -- Process all holders of this security
    FOR v_position_record IN
        SELECT id, user_id, quantity FROM positions
        WHERE security_id = p_security_id AND quantity > 0
    LOOP
        -- Calculate dividend
        v_total_amount := v_position_record.quantity * p_dividend_per_share;

        -- Add to user's cash balance
        UPDATE users SET
            cash_balance = cash_balance + v_total_amount,
            account_value = account_value + v_total_amount
        WHERE id = v_position_record.user_id;

        -- Update position's dividend income
        UPDATE positions SET
            dividend_income = dividend_income + v_total_amount,
            last_updated_at = CURRENT_TIMESTAMP
        WHERE id = v_position_record.id;

        -- Record transaction
        INSERT INTO transactions (
            user_id, security_id, transaction_type, quantity, price,
            amount, transaction_date, settled_date
        ) VALUES (
            v_position_record.user_id, p_security_id, 'dividend',
            v_position_record.quantity, p_dividend_per_share,
            v_total_amount, p_payment_date, p_payment_date
        );

        v_processed_count := v_processed_count + 1;
        v_total_amount := v_total_amount + v_total_amount;
    END LOOP;

    RETURN QUERY SELECT v_processed_count, v_total_amount;
END;
$$ LANGUAGE plpgsql;

-- Handle stock split
CREATE OR REPLACE FUNCTION process_stock_split(
    p_security_id INTEGER,
    p_split_ratio DECIMAL, -- e.g., 2 for 2:1 split
    p_split_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE(
    processed_positions INTEGER
) AS $$
DECLARE
    v_processed_count INTEGER := 0;
BEGIN
    -- Update all positions
    UPDATE positions SET
        quantity = quantity * p_split_ratio,
        average_cost_price = average_cost_price / p_split_ratio,
        cost_basis = quantity * p_split_ratio * (average_cost_price / p_split_ratio),
        market_value = (quantity * p_split_ratio) * current_price,
        last_updated_at = CURRENT_TIMESTAMP
    WHERE security_id = p_security_id AND quantity > 0;

    GET DIAGNOSTICS v_processed_count = ROW_COUNT;

    -- Record corporate action
    INSERT INTO transactions (
        user_id, security_id, transaction_type, quantity, amount,
        transaction_date, notes
    )
    SELECT
        user_id, p_security_id, 'stock_split', quantity, 0,
        p_split_date, 'Stock split: 1 share became ' || p_split_ratio::TEXT || ' shares'
    FROM positions
    WHERE security_id = p_security_id AND quantity > 0;

    RETURN QUERY SELECT v_processed_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. SCREENING & RESULT RECORDING PROCEDURES
-- ============================================================================

-- Record screener results
CREATE OR REPLACE FUNCTION record_screening_results(
    p_screener_id UUID,
    p_security_ids INTEGER[]
)
RETURNS TABLE(
    matched_count INTEGER
) AS $$
DECLARE
    v_security_id INTEGER;
    v_matched_count INTEGER := 0;
BEGIN
    -- Clear previous results from same screener on same day
    DELETE FROM screening_results
    WHERE screener_id = p_screener_id
    AND DATE(matched_at) = CURRENT_DATE;

    -- Insert new results
    FOREACH v_security_id IN ARRAY p_security_ids LOOP
        INSERT INTO screening_results (screener_id, security_id, matched_at)
        VALUES (p_screener_id, v_security_id, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING;

        v_matched_count := v_matched_count + 1;
    END LOOP;

    -- Update screener timestamp
    UPDATE screeners SET updated_at = CURRENT_TIMESTAMP
    WHERE id = p_screener_id;

    RETURN QUERY SELECT v_matched_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. DATA MAINTENANCE & CLEANUP PROCEDURES
-- ============================================================================

-- Archive quotes data to OHLC
CREATE OR REPLACE PROCEDURE archive_quotes_to_ohlc(p_date DATE DEFAULT CURRENT_DATE - 1)
LANGUAGE plpgsql
AS $$
DECLARE
    v_processed_count INTEGER := 0;
BEGIN
    -- This would aggregate daily quotes into OHLC if detailed tick data exists
    -- Implementation depends on your quote update frequency

    -- Example: daily OHLC from quotes
    INSERT INTO ohlc_data (security_id, period, open_time, open, high, low, close, volume)
    SELECT
        q.security_id,
        '1d' as period,
        DATE_TRUNC('day', q.timestamp) as open_time,
        FIRST(q.last_price ORDER BY q.timestamp) as open,
        MAX(q.high) as high,
        MIN(q.low) as low,
        LAST(q.last_price ORDER BY q.timestamp) as close,
        MAX(q.volume) as volume
    FROM quotes q
    WHERE DATE(q.timestamp) = p_date
    GROUP BY q.security_id, DATE_TRUNC('day', q.timestamp)
    ON CONFLICT DO NOTHING;

    GET DIAGNOSTICS v_processed_count = ROW_COUNT;
    RAISE NOTICE 'Archived % quote records to OHLC', v_processed_count;
END;
$$;

-- Cleanup old sessions
CREATE OR REPLACE PROCEDURE cleanup_expired_sessions()
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % expired sessions', v_deleted_count;
END;
$$;

-- ============================================================================
-- 8. USER ACCOUNT PROCEDURES
-- ============================================================================

-- Deposit funds to user account
CREATE OR REPLACE FUNCTION deposit_funds(
    p_user_id UUID,
    p_amount DECIMAL,
    p_reference VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    new_balance DECIMAL,
    message TEXT
) AS $$
DECLARE
    v_current_balance DECIMAL;
BEGIN
    SELECT cash_balance INTO v_current_balance FROM users
    WHERE id = p_user_id FOR UPDATE;

    IF v_current_balance IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::DECIMAL, 'User not found'::TEXT;
        RETURN;
    END IF;

    UPDATE users SET
        cash_balance = cash_balance + p_amount,
        account_value = account_value + p_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id
    RETURNING cash_balance INTO v_current_balance;

    -- Record transaction
    INSERT INTO transactions (
        user_id, security_id, transaction_type, amount,
        transaction_date, notes
    ) VALUES (
        p_user_id, NULL, 'deposit', p_amount,
        CURRENT_TIMESTAMP,
        COALESCE('Deposit: ' || p_reference, 'Deposit')
    );

    RETURN QUERY SELECT TRUE, v_current_balance, 'Deposit successful'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Withdraw funds from user account
CREATE OR REPLACE FUNCTION withdraw_funds(
    p_user_id UUID,
    p_amount DECIMAL,
    p_reference VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    new_balance DECIMAL,
    message TEXT
) AS $$
DECLARE
    v_current_balance DECIMAL;
BEGIN
    SELECT cash_balance INTO v_current_balance FROM users
    WHERE id = p_user_id FOR UPDATE;

    IF v_current_balance IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::DECIMAL, 'User not found'::TEXT;
        RETURN;
    END IF;

    IF v_current_balance < p_amount THEN
        RETURN QUERY SELECT FALSE, v_current_balance, 'Insufficient funds'::TEXT;
        RETURN;
    END IF;

    UPDATE users SET
        cash_balance = cash_balance - p_amount,
        account_value = account_value - p_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id
    RETURNING cash_balance INTO v_current_balance;

    -- Record transaction
    INSERT INTO transactions (
        user_id, security_id, transaction_type, amount,
        transaction_date, notes
    ) VALUES (
        p_user_id, NULL, 'withdrawal', p_amount,
        CURRENT_TIMESTAMP,
        COALESCE('Withdrawal: ' || p_reference, 'Withdrawal')
    );

    RETURN QUERY SELECT TRUE, v_current_balance, 'Withdrawal successful'::TEXT;
END;
$$ LANGUAGE plpgsql;
