# -*- coding: utf-8 -*-
{
    'name': "Price List Editing",

    'summary': "This model adding sales price and barcode fields to the sales price tree in pos",

    'description': """
This model adding sales price and barcode fields to the sales price tree in pos
    """,
    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'product', 'point_of_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

