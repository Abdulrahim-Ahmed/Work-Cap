# -*- coding: utf-8 -*-
{
    'name': "Auto Create Analytic Account In Lines ",

    'summary': "This module adds an Analytic Account field on invoices and bills",

    'description': """
This module adds an Analytic Account field on invoices and bills.  
When set, the chosen Analytic Account is automatically applied to all invoice/bill lines  
via the analytic distribution field, ensuring consistent analytic tracking without  
manually editing each line.    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

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

