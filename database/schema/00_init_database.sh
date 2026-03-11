#!/bin/bash
# ============================================================================
# Stock Exchange Board Database Initialization Script
# Usage: ./00_init_database.sh [environment]
# Environments: development, staging, production
# ============================================================================

set -e

# Configuration
ENVIRONMENT=${1:-development}
DB_NAME="stockexchange"
DB_USER="stockex_app"
DB_PORT="${DB_PORT:-5432}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Pre-flight checks
# ============================================================================

log_info "Initializing database for environment: $ENVIRONMENT"

# Check PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL client not found. Install pg-client first."
    exit 1
fi

# Check PostgreSQL version
PG_VERSION=$(psql --version | grep -oP 'postgres \(PostgreSQL\) \K[0-9]+')
if [ "$PG_VERSION" -lt 13 ]; then
    log_error "PostgreSQL 13+ required. Found version: $PG_VERSION"
    exit 1
fi

log_info "PostgreSQL version: $PG_VERSION ✓"

# ============================================================================
# Database and User Creation
# ============================================================================

log_info "Creating database user and database..."

# Create user (if not exists)
if ! psql -U postgres -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1; then
    log_info "Creating database user: $DB_USER"

    # Generate secure password
    DB_PASSWORD=$(openssl rand -base64 32)

    createuser --createdb --no-superuser $DB_USER
    psql -U postgres -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

    log_info "Database credentials created:"
    echo "   Username: $DB_USER"
    echo "   Password: $DB_PASSWORD"
    echo "   Save these credentials securely!"
else
    log_warn "User $DB_USER already exists"
    DB_PASSWORD="<existing>"
fi

# Create database (if not exists)
if ! psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
    log_info "Creating database: $DB_NAME"
    createdb -O $DB_USER -E UTF8 -l en_US.UTF-8 $DB_NAME
else
    log_warn "Database $DB_NAME already exists"
fi

log_info "Database setup complete ✓"

# ============================================================================
# Extensions and Configuration
# ============================================================================

log_info "Enabling PostgreSQL extensions..."

psql -U postgres -d $DB_NAME << EOF
\set ON_ERROR_STOP on

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set application user permissions
GRANT CREATE ON DATABASE $DB_NAME TO $DB_USER;
GRANT USAGE ON SCHEMA public TO $DB_USER;
GRANT CREATE ON SCHEMA public TO $DB_USER;

-- Allow user to create tables
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public
    GRANT ALL ON TABLES TO $DB_USER;

ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public
    GRANT ALL ON SEQUENCES TO $DB_USER;

ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public
    GRANT ALL ON FUNCTIONS TO $DB_USER;
EOF

log_info "Extensions enabled ✓"

# ============================================================================
# Schema Creation
# ============================================================================

log_info "Creating database schema..."

# Execute schema scripts in order
SCRIPTS=(
    "01_core_tables.sql"
    "03_views_and_queries.sql"
    "04_stored_procedures.sql"
)

for script in "${SCRIPTS[@]}"; do
    SCRIPT_PATH="$SCRIPT_DIR/$script"

    if [ ! -f "$SCRIPT_PATH" ]; then
        log_error "Script not found: $SCRIPT_PATH"
        exit 1
    fi

    log_info "Executing: $script"
    psql -U $DB_USER -d $DB_NAME -f "$SCRIPT_PATH" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log_info "  ✓ $script"
    else
        log_error "Failed to execute: $script"
        exit 1
    fi
done

log_info "Schema creation complete ✓"

# ============================================================================
# Reference Data
# ============================================================================

log_info "Inserting reference data..."

psql -U $DB_USER -d $DB_NAME << 'EOF'
\set ON_ERROR_STOP on

-- Exchanges
INSERT INTO exchanges (code, name, country, timezone, opening_time, closing_time, is_active)
VALUES
    ('NYSE', 'New York Stock Exchange', 'United States', 'America/New_York', '09:30'::TIME, '16:00'::TIME, true),
    ('NASDAQ', 'NASDAQ', 'United States', 'America/New_York', '09:30'::TIME, '16:00'::TIME, true),
    ('AMEX', 'American Stock Exchange', 'United States', 'America/New_York', '09:30'::TIME, '16:00'::TIME, true),
    ('LSE', 'London Stock Exchange', 'United Kingdom', 'Europe/London', '08:00'::TIME, '16:30'::TIME, true),
    ('TSE', 'Tokyo Stock Exchange', 'Japan', 'Asia/Tokyo', '09:00'::TIME, '15:00'::TIME, true),
    ('HKE', 'Hong Kong Exchanges', 'Hong Kong', 'Asia/Hong_Kong', '09:30'::TIME, '16:00'::TIME, true)
ON CONFLICT (code) DO NOTHING;

-- Indicators
INSERT INTO indicators (name, description, calculation_method, parameters)
VALUES
    ('SMA_20', '20-period Simple Moving Average', 'SUM(close) / 20', '{"period": 20}'::JSONB),
    ('SMA_50', '50-period Simple Moving Average', 'SUM(close) / 50', '{"period": 50}'::JSONB),
    ('SMA_200', '200-period Simple Moving Average', 'SUM(close) / 200', '{"period": 200}'::JSONB),
    ('RSI_14', '14-period Relative Strength Index', 'Complex momentum calculation', '{"period": 14}'::JSONB),
    ('MACD', 'Moving Average Convergence Divergence', 'EMA(12) - EMA(26)', '{"fast": 12, "slow": 26, "signal": 9}'::JSONB),
    ('BB_20', 'Bollinger Bands 20-period', 'SMA +/- 2*StdDev', '{"period": 20, "std_dev": 2}'::JSONB)
ON CONFLICT (name) DO NOTHING;

-- Market indices
INSERT INTO indices (symbol, name, description, index_type, country, base_value, base_date)
VALUES
    ('INDU', 'Dow Jones Industrial Average', 'Large-cap US stocks', 'broad_market', 'United States', 10000, '1896-05-26'),
    ('GSPC', 'S&P 500', 'Large-cap US stocks', 'broad_market', 'United States', 10, '1957-03-04'),
    ('CCMP', 'NASDAQ Composite', 'Tech-heavy US stocks', 'broad_market', 'United States', 100, '1971-02-05'),
    ('RUT', 'Russell 2000', 'Small-cap US stocks', 'broad_market', 'United States', 100, '1984-12-31'),
    ('VIX', 'Volatility Index', 'Market volatility gauge', 'volatility', 'United States', 0, '1993-01-01')
ON CONFLICT (symbol) DO NOTHING;

-- System configuration
INSERT INTO system_config (config_key, config_value, config_type, description)
VALUES
    ('market_open_time', '09:30', 'string', 'US Market opening time (HH:MM)'),
    ('market_close_time', '16:00', 'string', 'US Market closing time (HH:MM)'),
    ('quote_update_interval_seconds', '1', 'integer', 'Quote update frequency'),
    ('ohlc_aggregation_enabled', 'true', 'boolean', 'Auto-aggregate quotes to OHLC'),
    ('data_retention_days_quotes', '30', 'integer', 'Retain detailed quotes for N days'),
    ('data_retention_days_ohlc', '1095', 'integer', 'Retain OHLC data for N days (3 years)'),
    ('max_concurrent_orders_per_user', '100', 'integer', 'Maximum open orders per user')
ON CONFLICT (config_key) DO NOTHING;

COMMIT;
EOF

log_info "Reference data inserted ✓"

# ============================================================================
# Partitioning (for non-MVP)
# ============================================================================

if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    log_info "Setting up table partitioning (production)..."

    PARTITION_SCRIPT="$SCRIPT_DIR/02_partitioning_strategy.sql"
    if [ -f "$PARTITION_SCRIPT" ]; then
        psql -U $DB_USER -d $DB_NAME -f "$PARTITION_SCRIPT" > /dev/null 2>&1
        log_info "Partitioning setup complete ✓"
    else
        log_warn "Partitioning script not found: $PARTITION_SCRIPT"
    fi
fi

# ============================================================================
# Verification
# ============================================================================

log_info "Verifying schema..."

TABLE_COUNT=$(psql -U $DB_USER -d $DB_NAME -tc \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" \
    | tr -d ' ')

VIEW_COUNT=$(psql -U $DB_USER -d $DB_NAME -tc \
    "SELECT COUNT(*) FROM information_schema.views WHERE table_schema='public';" \
    | tr -d ' ')

FUNC_COUNT=$(psql -U $DB_USER -d $DB_NAME -tc \
    "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema='public';" \
    | tr -d ' ')

log_info "Schema verification:"
echo "   Tables created: $TABLE_COUNT"
echo "   Views created: $VIEW_COUNT"
echo "   Functions/Procedures: $FUNC_COUNT"

if [ "$TABLE_COUNT" -lt 30 ]; then
    log_warn "Expected 30+ tables, found $TABLE_COUNT"
fi

# ============================================================================
# Summary
# ============================================================================

log_info ""
log_info "========================================"
log_info "Database initialization complete!"
log_info "========================================"
log_info ""
log_info "Connection details:"
log_info "   Database: $DB_NAME"
log_info "   User: $DB_USER"
log_info "   Host: localhost"
log_info "   Port: $DB_PORT"
log_info ""
log_info "Test connection:"
log_info "   psql -U $DB_USER -d $DB_NAME -h localhost"
log_info ""

if [ "$ENVIRONMENT" = "development" ]; then
    log_info "Next steps:"
    log_info "   1. Update .env with database credentials"
    log_info "   2. Start application with: npm run dev"
    log_info "   3. Run migrations if needed: npm run migrate"
fi

if [ "$ENVIRONMENT" = "production" ]; then
    log_warn ""
    log_warn "PRODUCTION SETUP NOTES:"
    log_warn "   - Enable SSL in postgresql.conf"
    log_warn "   - Configure pg_hba.conf for remote access"
    log_warn "   - Set up continuous backups"
    log_warn "   - Configure monitoring and alerting"
    log_warn "   - Schedule pg_cron maintenance jobs"
    log_warn ""
fi

exit 0
