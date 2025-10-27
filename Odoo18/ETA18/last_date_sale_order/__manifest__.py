# -*- coding: utf-8 -*-
{
    'name': "last_date_sale_order",
    'summary': """   """,
    'description': """    """,
    'author': "Basem walid",
    'website': "",
    'category': 'Services',
    'version': '18.0.1.0.0',
    'license': "AGPL-3",
    'depends': ['base', 'sale',  'sale_management',],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/date_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
