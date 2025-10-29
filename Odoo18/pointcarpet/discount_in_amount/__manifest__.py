# -*- coding: utf-8 -*-
{
    'name': "Discount In Amount",

    'summary': "This module is adding a discount by amount in sale order tree & po tree to calculate discount by "
               "amount and to "
               "edit the standard discount field to be 4 digits after decimal point then update it in invoice also",

    'description': """
    This module is adding a discount by amount in sale order tree & po tree to calculate discount by "
               "amount and to "
               "edit the standard discount field to be 4 digits after decimal point then update it in invoice also""",

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale', 'purchase', 'account'],
    'data': [
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'report/saleorderreport.xml',
        'report/invoice_printing.xml',
        'report/purchase_order_report.xml',
        'report/purchase_quotation_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
