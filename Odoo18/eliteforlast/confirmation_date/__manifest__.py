# -*- coding: utf-8 -*-
{
    'name': "Confirmation Date",

    'summary': "This module adds a confirmation_date field to both Sales Orders and the Sales Report.",

    'description': """
This module adds a confirmation_date field to both Sales Orders and the Sales Report.
When a sales order is confirmed, the current datetime is automatically recorded in the confirmation_date field.
The same field is included in the sales analysis report (sale.report) for reporting and filtering purposes.
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

