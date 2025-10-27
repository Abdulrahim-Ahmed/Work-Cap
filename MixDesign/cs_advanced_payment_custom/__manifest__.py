# -*- coding: utf-8 -*-
{
    'name': "Advanced Payment Custom",

    'summary': "Advanced payment functionality with custom journal entries",

    'description': """
Advanced Payment Custom Module
==============================
This module adds advanced payment functionality to Odoo 18:
- Duplicate payment menus for customer and vendor sections
- Configuration fields for vendor_debit and customer_credit accounts
- Custom journal entry logic for advanced payments
    """,

    'author': "My Company",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/account_config_settings_views.xml',
        'views/advanced_payment_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
