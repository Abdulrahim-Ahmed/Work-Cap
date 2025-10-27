# -*- coding: utf-8 -*-
{
    'name': "cs_invoice_fields",

    'summary': "adding extra fields in invoices tree view",

    'description': """
adding extra fields in invoices tree view
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','contacts','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # 'assets': {
    # 'point_of_sale._assets_pos': [
    # 'cs_invoice_fields/static/src/**/*',
    # ],
    # },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
