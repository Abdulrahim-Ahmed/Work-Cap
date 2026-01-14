# -*- coding: utf-8 -*-
{
    'name': "Custom Operations Report",

    'summary': "Comprehensive operations report with sales, purchases, and profitability analysis",

    'description': """
Custom Operations Report Module
===============================
This module provides a comprehensive operations report that includes:
- Sales and purchase order analysis
- Profitability calculations
- Product performance tracking
- Customer and vendor reporting
- Financial summaries and analytics
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'account', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/operations_report_wizard_view.xml',
        'report/report.xml',
        'report/operations_report_template.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

