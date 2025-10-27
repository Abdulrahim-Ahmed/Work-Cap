# Multi Currency Partner Ledger Documentation

![DigitsCode Logo](../static/DigitsCode.png)

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Guide](#usage-guide)
5. [Technical Details](#technical-details)
6. [Troubleshooting](#troubleshooting)
7. [Support](#support)

## Introduction <a name="introduction"></a>

The Multi Currency Partner Ledger module for Odoo 18 allows businesses to generate detailed partner ledger reports in multiple currencies. This comprehensive documentation provides all the information needed to install, configure, and use the module effectively.

### Key Features

- **Multi-Currency Support**: View partner ledger reports in multiple currencies simultaneously
- **Flexible Filtering**: Filter by partner, date range, account, and target moves
- **Initial Balances**: Option to show initial balances for comprehensive reporting
- **Export Options**: Export reports to PDF and Excel formats
- **Detailed Transaction View**: See all transactions by currency with clear debit, credit, and balance columns
- **User-Friendly Interface**: Intuitive wizard interface for easy report generation

## Installation <a name="installation"></a>

### Prerequisites
- Odoo 18 Enterprise Edition
- Python 3.10 or higher
- Required dependencies: account, web, report_xlsx

### Installation Steps

1. Download the module from the Odoo Apps store or copy it to your custom addons directory
2. Update the apps list in Odoo:
   - Go to Apps menu
   - Click on "Update Apps List" in the top menu
   - Click "Update" in the dialog
3. Install the module:
   - Search for "Multi Currency Partner Ledger" in the Apps menu
   - Click "Install" button
4. Restart the Odoo server to ensure all changes take effect

## Configuration <a name="configuration"></a>

The Multi Currency Partner Ledger module requires minimal configuration. However, to ensure optimal functionality, follow these steps:

1. **Set Up Currencies**:
   - Go to Accounting → Configuration → Currencies
   - Ensure all required currencies are activated
   - Verify that exchange rates are up-to-date

2. **Configure User Access Rights**:
   - Go to Settings → Users & Companies → Users
   - Edit the user(s) who need access to the module
   - Ensure they have access to Accounting features
   - Save changes

3. **Optional: Default Settings**:
   - Go to Accounting → Configuration → Settings
   - Configure default fiscal year settings
   - Set up default accounts if needed

## Usage Guide <a name="usage-guide"></a>

### Generating a Multi-Currency Partner Ledger Report

1. Navigate to Accounting → Reporting → Multi Currency Partner Ledger
2. In the wizard form, set the following parameters:
   - **Date Range**: Select start and end dates for the report
   - **Target Moves**: Choose between "All Posted Entries" or "All Entries"
   - **Partners**: Select specific partners or leave blank for all
   - **Accounts**: Select specific accounts or leave blank for all
   - **Currencies**: Select the currencies to include in the report
   - **Show Initial Balance**: Toggle to show or hide initial balances
   - **Reconciled**: Option to show only reconciled entries

3. Click one of the following buttons:
   - **View**: Display the report in the browser
   - **Print**: Generate a PDF report
   - **Export Excel**: Download an Excel (XLSX) version of the report

### Understanding the Report

The Multi Currency Partner Ledger report displays the following information:

- **Header**: Company information, report date range, and filter criteria
- **Partner Information**: Partner name, code, and contact details
- **Currency Sections**: Separate sections for each selected currency
- **Transaction Details**: Date, journal, reference, label, debit, credit, and balance
- **Subtotals**: Subtotals per currency and partner
- **Grand Total**: Total across all partners and currencies

## Technical Details <a name="technical-details"></a>

### Module Structure

The module is organized as follows:

- **models/**: Contains the data models
  - `account_move_line.py`: Extends account move line model
  - `multi_currency_ledger.py`: Main report model
- **wizard/**: Contains the report wizard
  - `multi_currency_ledger_wizard.py`: Wizard model and views
- **report/**: Contains report templates and rendering logic
  - `multi_currency_ledger_report.xml`: Report action definitions
  - `multi_currency_ledger_report_templates.xml`: QWeb templates for PDF
  - `multi_currency_ledger_report_xlsx.py`: Excel report generator
- **security/**: Contains access control definitions
  - `ir.model.access.csv`: Access rights configuration
- **views/**: Contains UI views
  - `menu_views.xml`: Menu definitions
- **static/**: Contains static assets
  - `description/`: Module description and screenshots
  - `Screenshot/`: Additional screenshots

### Technical Implementation

The module implements the following technical features:

1. **Custom Report Model**: Extends AbstractModel to create a flexible report
2. **XLSX Report Generation**: Uses report_xlsx module to create Excel reports
3. **Multi-Currency Calculations**: Performs currency conversions and calculations
4. **QWeb Templates**: Uses QWeb for PDF report generation
5. **Wizard Interface**: Provides a user-friendly interface for report configuration

## Troubleshooting <a name="troubleshooting"></a>

### Common Issues and Solutions

1. **Report Shows No Data**
   - Verify that partners have transactions in the selected date range
   - Check that the selected currencies are used in transactions
   - Ensure accounts contain transactions for the selected partners

2. **Currency Amounts Are Incorrect**
   - Verify exchange rates are correctly set up in Odoo
   - Check the transaction dates match the exchange rate dates
   - Ensure the base currency is properly configured

3. **Excel Export Fails**
   - Verify the report_xlsx module is properly installed
   - Check server logs for specific error messages
   - Ensure the user has proper access rights

4. **Performance Issues with Large Datasets**
   - Consider narrowing the date range
   - Filter by specific partners rather than all
   - Select only relevant currencies

### Error Messages

| Error Message | Possible Cause | Solution |
|---------------|----------------|----------|
| "No data available" | No transactions found for the selected criteria | Adjust filter criteria |
| "Currency rate missing" | Exchange rate not defined for a date | Set up the missing exchange rate |
| "Access denied" | Insufficient user permissions | Grant proper access rights |

## Support <a name="support"></a>

For any questions, issues, or feature requests, please contact:

- **Email**: info@digitscode.com
- **Website**: https://www.digitscode.com
- **Phone**: Contact your account manager

### Reporting Bugs

When reporting bugs, please include:
1. Detailed description of the issue
2. Steps to reproduce
3. Screenshots if applicable
4. Odoo version and module version
5. Browser information (if web-related)

---

© 2025 Digital Integrated Transformation Solutions (DigitsCode)  
This module is licensed under the Odoo Proprietary License (OPL-1).
