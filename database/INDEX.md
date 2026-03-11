# Database Schema Documentation Index

Complete reference guide to the Stock Exchange Board PostgreSQL database schema.

## Quick Navigation

### Getting Started
- **[README.md](./README.md)** - Installation, quick start, basic troubleshooting
- **[SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md)** - Complete package overview
- **[schema/00_init_database.sh](./schema/00_init_database.sh)** - Automated setup script

### Core Documentation
1. **[schema/01_core_tables.sql](./schema/01_core_tables.sql)** - All table definitions (30+)
2. **[schema/02_partitioning_strategy.sql](./schema/02_partitioning_strategy.sql)** - Table partitioning
3. **[schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)** - Views and materialized views
4. **[schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)** - Business logic procedures
5. **[schema/07_index_optimization.sql](./schema/07_index_optimization.sql)** - Performance indexes

### Advanced Documentation
- **[schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md)** - Architecture & ERD
- **[schema/06_migration_guide.md](./schema/06_migration_guide.md)** - Deployment procedures

---

## By Role

### Database Administrator

**First Steps:**
1. Read [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Overview
2. Review [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Architecture
3. Execute [schema/00_init_database.sh](./schema/00_init_database.sh) - Setup

**Ongoing:**
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Maintenance procedures
- [schema/07_index_optimization.sql](./schema/07_index_optimization.sql) - Performance tuning
- [README.md](./README.md) - Troubleshooting section

### Backend Developer

**First Steps:**
1. Read [README.md](./README.md) - Connection setup
2. Review [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Data model
3. Study [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql) - Available views
4. Understand [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql) - Business logic

**Query Development:**
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Query examples (section 9)
- [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql) - Pre-built views

### Application Developer

**First Steps:**
1. Quick read [README.md](./README.md) - Quick start
2. Check [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Table inventory
3. Reference [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Entity relationships

**Common Tasks:**
- Get portfolio data → Use `v_user_portfolio_summary` view
- Execute order → Call `execute_market_order()` procedure
- Find user positions → Query `v_user_positions_detailed` view
- Check alerts → Query `v_active_price_alerts` view

### DevOps/Infrastructure

**Deployment:**
1. [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Phase 1 deployment
2. [schema/00_init_database.sh](./schema/00_init_database.sh) - Automated setup
3. [README.md](./README.md) - Monitoring section

**Production:**
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Production setup
- Configure pg_cron jobs (in README.md)
- Set up monitoring alerts (in migration guide)

---

## By Topic

### Database Setup
- [schema/00_init_database.sh](./schema/00_init_database.sh) - Automated initialization
- [README.md](./README.md) - Quick start
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Detailed deployment

### Table Structure
- [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Table inventory
- [schema/01_core_tables.sql](./schema/01_core_tables.sql) - Definitions
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Entity relationships

### Querying Data
- [README.md](./README.md) - Query examples
- [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql) - All views
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Query examples

### Business Logic
- [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql) - Procedures
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Logic overview

### Performance
- [README.md](./README.md) - Performance targets
- [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql) - Materialized views
- [schema/07_index_optimization.sql](./schema/07_index_optimization.sql) - Indexes
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Optimization strategies

### Scaling
- [schema/02_partitioning_strategy.sql](./schema/02_partitioning_strategy.sql) - Partitioning
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Scalability architecture
- [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Scaling metrics

### Compliance & Audit
- [schema/01_core_tables.sql](./schema/01_core_tables.sql) - audit_logs, transaction_audit_trail tables
- [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Compliance section
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Compliance setup

### Deployment & Rollback
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Complete deployment guide
- [README.md](./README.md) - Quick troubleshooting

### Data Retention & Archival
- [schema/02_partitioning_strategy.sql](./schema/02_partitioning_strategy.sql) - Archival procedures
- [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql) - `archive_old_ohlc_data()`
- [schema/06_migration_guide.md](./schema/06_migration_guide.md) - Backup strategies

---

## Key Concepts Reference

### Data Models

**User Account Model**
→ [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Section 2

**Portfolio Model**
→ [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Section 2

**Market Data Model**
→ [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) - Section 2

**Order Execution Model**
→ [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql) - `execute_market_order()`

### Views

**Portfolio Views**
```
v_user_portfolio_summary          -- Account summary
v_user_positions_detailed         -- Holdings with prices
v_user_trading_activity           -- Transaction history
v_dividend_income_summary         -- Dividend tracking
```
→ [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

**Market Data Views**
```
v_security_market_data            -- Current prices & metrics
v_sector_performance              -- Sector aggregates
v_index_performance               -- Index values
```
→ [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

**Alert & Monitoring Views**
```
v_active_price_alerts             -- Triggered alerts
v_screener_results_with_data      -- Screening matches
```
→ [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

### Stored Procedures

**Order Management**
```
execute_market_order()            -- Execute order atomically
```
→ [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

**Portfolio Operations**
```
calculate_portfolio_valuation()   -- P&L snapshot
deposit_funds()                   -- Add cash
withdraw_funds()                  -- Remove cash
```
→ [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

**Alert & Screening**
```
check_price_alerts()              -- Check triggered alerts
record_screening_results()        -- Store screener matches
```
→ [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

### Indexes

**Critical Performance Indexes** (12)
→ [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) - Index Summary

**Advanced Optimization Indexes** (50+)
→ [schema/07_index_optimization.sql](./schema/07_index_optimization.sql)

---

## File Reference

### Core Schema Files

| File | Purpose | Key Content |
|------|---------|------------|
| [01_core_tables.sql](./schema/01_core_tables.sql) | Table definitions | 30+ tables, constraints, basic indexes |
| [02_partitioning_strategy.sql](./schema/02_partitioning_strategy.sql) | Partitioning | Partition setup, archival strategies |
| [03_views_and_queries.sql](./schema/03_views_and_queries.sql) | Views | 20+ views, materialized views |
| [04_stored_procedures.sql](./schema/04_stored_procedures.sql) | Business logic | 20+ procedures, atomic operations |
| [07_index_optimization.sql](./schema/07_index_optimization.sql) | Performance | 50+ indexes, analysis functions |

### Documentation Files

| File | Purpose | Key Content |
|------|---------|------------|
| [README.md](./README.md) | Quick start | Setup, architecture, examples |
| [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) | Overview | Complete package summary |
| [05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) | Architecture | ERD, design decisions, examples |
| [06_migration_guide.md](./schema/06_migration_guide.md) | Deployment | Phase-by-phase deployment |

---

## Common Tasks - Quick Reference

### Setup Database
```bash
cd database/schema
chmod +x 00_init_database.sh
./00_init_database.sh development
```
→ See [README.md](./README.md) for details

### Query User Portfolio
```sql
SELECT * FROM v_user_portfolio_summary WHERE user_id = 'xxx';
```
→ See [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) section 9

### Execute an Order
```sql
SELECT execute_market_order(order_id, quantity, price, NOW());
```
→ See [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

### Get Market Data
```sql
SELECT * FROM v_security_market_data WHERE symbol = 'AAPL';
```
→ See [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

### Deploy to Production
→ See [schema/06_migration_guide.md](./schema/06_migration_guide.md) section 3

### Troubleshoot Performance
→ See [README.md](./README.md) - Troubleshooting section

### Add New Indexes
→ See [schema/07_index_optimization.sql](./schema/07_index_optimization.sql)

### Schedule Maintenance
→ See [schema/06_migration_guide.md](./schema/06_migration_guide.md) section 8

---

## Document Size Reference

| Document | Lines | Purpose |
|----------|-------|---------|
| README.md | 400 | Quick start & reference |
| SCHEMA_SUMMARY.md | 800 | Complete overview |
| 01_core_tables.sql | 1000+ | Table definitions |
| 02_partitioning_strategy.sql | 400 | Partitioning setup |
| 03_views_and_queries.sql | 1000+ | Views definitions |
| 04_stored_procedures.sql | 1000+ | Procedure implementations |
| 05_erd_and_design_docs.md | 1000+ | Architecture & design |
| 06_migration_guide.md | 1500+ | Deployment procedures |
| 07_index_optimization.sql | 500+ | Performance indexes |
| **Total** | **7600+** | **Complete documentation** |

---

## Search Guide

### Looking for...

**Table Definitions**
→ [schema/01_core_tables.sql](./schema/01_core_tables.sql)

**Performance Optimization**
→ [schema/07_index_optimization.sql](./schema/07_index_optimization.sql)

**Query Examples**
→ [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) section 9

**Deployment Steps**
→ [schema/06_migration_guide.md](./schema/06_migration_guide.md)

**Data Model**
→ [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md) or [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) section 2

**Entity Relationships**
→ [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md) section 2

**Stored Procedures**
→ [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

**Views & Queries**
→ [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

**Partitioning Strategy**
→ [schema/02_partitioning_strategy.sql](./schema/02_partitioning_strategy.sql)

**Monitoring & Alerts**
→ [schema/06_migration_guide.md](./schema/06_migration_guide.md) section 9

**Troubleshooting**
→ [README.md](./README.md) or [schema/06_migration_guide.md](./schema/06_migration_guide.md) section 10

---

## Getting Help

1. **Check the relevant documentation** - Use the index above to find the right document
2. **Search for specific table/view/procedure** - Listed in [SCHEMA_SUMMARY.md](./SCHEMA_SUMMARY.md)
3. **Review example queries** - In [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md)
4. **Check troubleshooting** - In [README.md](./README.md) and migration guide
5. **Review stored procedures** - In [schema/04_stored_procedures.sql](./schema/04_stored_procedures.sql)

---

## Version Information

- **Schema Version:** 1.0.0
- **PostgreSQL Version:** 13+
- **Created:** 2026-03-10
- **Status:** Production Ready
- **Total Tables:** 30+
- **Total Views:** 20+
- **Total Procedures:** 20+
- **Total Indexes:** 50+

---

## Next Steps

1. **First time?** → Start with [README.md](./README.md)
2. **Need setup?** → Use [schema/00_init_database.sh](./schema/00_init_database.sh)
3. **Want architecture?** → Read [schema/05_erd_and_design_docs.md](./schema/05_erd_and_design_docs.md)
4. **Going to production?** → Follow [schema/06_migration_guide.md](./schema/06_migration_guide.md)
5. **Writing queries?** → Check [schema/03_views_and_queries.sql](./schema/03_views_and_queries.sql)

