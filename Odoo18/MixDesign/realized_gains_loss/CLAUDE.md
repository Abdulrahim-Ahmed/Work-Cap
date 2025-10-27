# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Odoo 18 development environment with a custom addon `realized_gains_loss` that extends the Multicurrency Revaluation Report to add realized currency gains/losses functionality. The project is located within `/opt/odoo18/new_customs/realized_gains_loss/` and inherits from Odoo's `account.multicurrency.revaluation.report.handler`.

## Architecture

### Directory Structure
- `/opt/odoo18/` - Main Odoo 18 installation
  - `addons/` - Standard Odoo addons
  - `enterprise/` - Enterprise addons  
  - `new_customs/` - Custom addons directory containing:
    - `realized_gains_loss/` - The main custom addon
- `odoo18.conf` - Odoo configuration file
- `requirements.txt` - Python dependencies

### Key Components

**Models (`models/models.py`)**
- `MulticurrencyRevaluationReportCustomHandler` - Extends `account.multicurrency.revaluation.report.handler`
- Implements realized currency gains/losses calculation using actual payment dates and exchange rates
- Key methods:
  - `_report_custom_engine_realized_currency_gains()` - Handles gains calculations
  - `_report_custom_engine_realized_currency_losses()` - Handles losses calculations  
  - `_realized_currency_get_custom_lines()` - Core SQL logic for realized exchange differences

**Module Structure**
- Standard Odoo addon structure with `__manifest__.py`, models, views, controllers
- Depends on: `['base', 'accountant']`
- Uses UTF-8 encoding throughout

## Development Commands

### Starting Odoo
```bash
cd /opt/odoo18
python3 odoo-bin -c odoo18.conf
```

### Installing/Upgrading the Module
```bash
# Install
python3 odoo-bin -c odoo18.conf -i realized_gains_loss

# Upgrade 
python3 odoo-bin -c odoo18.conf -u realized_gains_loss
```

### Database Management
```bash
# Create new database
python3 odoo-bin -c odoo18.conf -d new_db --init base

# Database configuration from odoo18.conf:
# - Host: localhost:5432
# - User: odoo18
# - Default port: 8018
```

### Development Mode
```bash
# Run with development mode and auto-reload
python3 odoo-bin -c odoo18.conf --dev=all --log-level=debug
```

## Key Technical Details

### SQL Implementation
The module uses complex SQL queries with:
- Lateral joins to get currency rates at payment dates
- Exchange move reconciliation tracking
- Period-based filtering for realized gains/losses
- Account type filtering (receivable/payable only)

### Currency Rate Logic
- Uses `res_currency_rate` table for historical rates
- Compares payment-date rates vs original transaction rates
- Calculates actual realized exchange differences on settlement

### Report Integration
Extends Odoo's multicurrency revaluation reporting framework with custom line handlers for gains and losses segregation.

## Configuration Notes

- Python version compatibility: 3.10-3.12+ (see requirements.txt)
- Database: PostgreSQL required
- Memory limits: 2GB soft / 2.5GB hard
- Time limits: 1200s CPU / 1800s real
- Addons path includes custom addons in `/opt/odoo18/new_customs/`

## Debugging Exchange Rate Issues

### Debugging Queries for Balance at Current Rate

If the Balance at Current Rate is showing incorrect values, use these debugging queries:

**1. Check payment reconciliation dates and currency rates:**
```sql
SELECT 
    aml.id as move_line_id,
    aml.name,
    aml.currency_id,
    aml.amount_currency,
    aml.balance,
    part.max_date as payment_date,
    part.id as partial_reconcile_id
FROM account_move_line aml
JOIN account_partial_reconcile part ON (part.debit_move_id = aml.id OR part.credit_move_id = aml.id)
WHERE aml.currency_id != aml.company_currency_id
  AND part.max_date BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'
ORDER BY part.max_date DESC;
```

**2. Check available currency rates for specific currency and date:**
```sql
SELECT 
    rate.name as rate_date,
    rate.rate,
    rate.currency_id,
    rate.company_id,
    curr.name as currency_name
FROM res_currency_rate rate
JOIN res_currency curr ON rate.currency_id = curr.id
WHERE rate.currency_id = <CURRENCY_ID>
  AND rate.name <= 'PAYMENT_DATE'
  AND (rate.company_id = <COMPANY_ID> OR rate.company_id IS NULL)
ORDER BY rate.name DESC, rate.company_id DESC NULLS LAST
LIMIT 5;
```

**3. Debug the exact rate used in calculation:**
```sql
SELECT 
    aml.id,
    aml.amount_currency,
    part.max_date,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM res_currency_rate r1 
            WHERE r1.currency_id = aml.currency_id 
              AND r1.name = part.max_date
              AND (r1.company_id = aml.company_id OR r1.company_id IS NULL)
        ) THEN (
            SELECT r2.rate 
            FROM res_currency_rate r2 
            WHERE r2.currency_id = aml.currency_id 
              AND r2.name = part.max_date
              AND (r2.company_id = aml.company_id OR r2.company_id IS NULL)
            ORDER BY r2.company_id DESC NULLS LAST
            LIMIT 1
        )
        ELSE (
            SELECT r3.rate 
            FROM res_currency_rate r3 
            WHERE r3.currency_id = aml.currency_id
              AND r3.name <= part.max_date
              AND (r3.company_id = aml.company_id OR r3.company_id IS NULL)
            ORDER BY r3.name DESC, r3.company_id DESC NULLS LAST
            LIMIT 1
        )
    END as used_rate,
    ABS(aml.amount_currency) / COALESCE(
        CASE 
            WHEN EXISTS (SELECT 1 FROM res_currency_rate r1 WHERE r1.currency_id = aml.currency_id AND r1.name = part.max_date AND (r1.company_id = aml.company_id OR r1.company_id IS NULL))
            THEN (SELECT r2.rate FROM res_currency_rate r2 WHERE r2.currency_id = aml.currency_id AND r2.name = part.max_date AND (r2.company_id = aml.company_id OR r2.company_id IS NULL) ORDER BY r2.company_id DESC NULLS LAST LIMIT 1)
            ELSE (SELECT r3.rate FROM res_currency_rate r3 WHERE r3.currency_id = aml.currency_id AND r3.name <= part.max_date AND (r3.company_id = aml.company_id OR r3.company_id IS NULL) ORDER BY r3.name DESC, r3.company_id DESC NULLS LAST LIMIT 1)
        END, 1.0
    ) as calculated_balance_current
FROM account_move_line aml
JOIN account_partial_reconcile part ON (part.debit_move_id = aml.id OR part.credit_move_id = aml.id)
WHERE aml.id = <SPECIFIC_MOVE_LINE_ID>;
```

**Key Changes Made:**
- Fixed rate calculation: currency_amount / rate (not multiply) - rates are stored as company_currency/foreign_currency
- Improved rate lookup to prioritize exact date matches
- Added fallback logic for company-specific vs global rates
- Enhanced rate selection with proper ordering

**Understanding Odoo Currency Rates:**
- Rates in res_currency_rate are stored as: 1 foreign_currency = rate * company_currency
- Example: If rate = 0.1492 for USD to EGP, it means 1 USD = 0.1492 EGP (INCORRECT)
- Actually: rate = 0.1492 means 1 EGP = 0.1492 USD, so 1 USD = 1/0.1492 = 6.7024 EGP
- Therefore: foreign_amount / rate = company_currency_amount

**Common Issues:**
- Rate direction: Odoo rates are inverted - divide foreign amount by rate, don't multiply
- Missing rates: Check if currency rates exist for the payment date
- Company context: Verify company_id matches in rate lookup
- **UI vs Database discrepancy**: The UI may show different rates than stored in res_currency_rate table
  - UI shows rates computed or cached differently
  - Always cross-reference UI rates with database rates using debugging queries
  - If rates don't match, investigate if UI connects to different DB or uses different calculation logic

**Example Discrepancy Resolution:**
- **Issue**: Database initially showed 2025-07-28 rate = 0.1492, but UI showed 0.02
- **Root Cause**: The UI displays computed fields (`company_rate` and `inverse_company_rate`) from the Currency Rates page
- **UI Fields**: 
  - "Unit per EGP" = `company_rate` (stored as `rate` field)
  - "EGP per Unit" = `inverse_company_rate` (computed as 1/rate)
- **Resolution**: Updated database rates to match UI values:
  - 2025-07-28: rate = 0.02 (1 USD = 50 EGP)
  - 2025-07-29: rate = 0.01666666 (1 USD = 60 EGP)
- **Result**: Calculation now works correctly with proper realized gains/losses

## Testing

The module focuses on accounting reconciliation scenarios, particularly:
- Foreign currency invoice/payment matching
- Exchange rate differences on payment dates
- Proper separation of realized vs unrealized gains/losses

No specific test framework is configured - use standard Odoo testing patterns with `unittest` and Odoo's test decorators.