# -*- coding: utf-8 -*-
{
    'name': "Company Filter for Product & POS Categories",
    'summary': "Add company field to product and POS categories for multi-company filtering",
    'description': """This module adds company field to product categories and POS categories to enable multi-company filtering""",
    'author': "Eng Abdulrahim: Capstone Solutions",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'depends': ['base', 'product', 'point_of_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/pos_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
