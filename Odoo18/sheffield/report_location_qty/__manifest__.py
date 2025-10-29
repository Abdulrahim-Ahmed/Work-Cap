# -*- coding: utf-8 -*-
{
    'name': "Product Location Report",
    'summary': """ Generate a report of product quantities across warehouses """,
    'description': """ """,
    'author': "Abd Elhamed Saad",
    'website': "https://www.linkedin.com/in/abd-elhamed-saad/",
    'category': 'Services',
    'version': '18.0.1.0.0',
    'license': "LGPL-3",
    'depends': ['base', 'stock', 'product', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_menu.xml',

        'views/stock_location.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
