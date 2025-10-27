# -*- coding: utf-8 -*-
{
    'name': 'Multi Currency Partner Ledger',
    'summary': 'Generate partner ledger reports with multiple currencies',
    'description': """
Multi Currency Partner Ledger
=============================
Generate partner ledger reports with multiple currencies.

Key Features
------------
* View partner ledger reports in multiple currencies
* Filter by partner, date range, and account
* Show initial balances
* Export to PDF and Excel
* Detailed view of transactions by currency
* Avoid currency exchange hassles

Technical Features
-----------------
* Advanced currency handling
* Real-time currency conversion
* Optimized report generation
* Enhanced data filtering
* Excel export with formatting (direct xlsxwriter, no report_xlsx dependency)
* PDF report with QWeb templates
* [2025-05-04] Direct Excel export and currency handling improvements. Removed report_xlsx dependency. Ensured Excel matches PDF structure and values are in selected currency.
    """,
    'version': '18.0.1.1.0',
    'author': 'Digital Integrated Transformation Solutions (DigitsCode)',
    'maintainer': 'Digital Integrated Transformation Solutions (DigitsCode)',
    'website': 'https://www.digitscode.com',
    'email': 'info@digitscode.com',
    'company': 'Digital Integrated Transformation Solutions (DigitsCode)',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'depends': [
        'account',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/multi_currency_ledger_wizard_views.xml',
        'report/multi_currency_ledger_report.xml',
        'report/multi_currency_ledger_report_templates.xml',
        'views/menu_views.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'price': 7,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}