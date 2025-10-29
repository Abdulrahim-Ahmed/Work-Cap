# -*- coding: utf-8 -*-
{
    'name': "po_number",

    'summary': """po_number""",

    'description': """po_number""",

    'author': "Basem Walid",
    'website': "http://www.deverst.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'stock'],

    # always loaded
    'data': [
        'views/pos_numbers.xml',
        'reports/sale_report_inherit.xml',
        'reports/sale_order_inherit.xml',
        'reports/sale_report_inherit_RFQ.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
