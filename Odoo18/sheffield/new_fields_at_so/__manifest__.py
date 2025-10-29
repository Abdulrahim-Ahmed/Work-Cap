# -*- coding: utf-8 -*-
{
    'name': "Shipping Company Fields",

    'summary': "Shipping Company Fields",

    'description': """
Shipping Company Fields
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'depends': ['base','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

