# -*- coding: utf-8 -*-
{
    'name': "cs_hide_pos_fields",

    'summary': "Override POS Quotation/Order action to show minimal sales order view",

    'description': """
This module overrides the default Quotation/Order action in POS to display a minimal sales order view 
that only shows order reference, order date, and customer information.
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solution.com",

    'category': 'Point of Sale',
    'version': '18.0.1.0.0',

    # Dependencies
    'depends': ['base', 'sale', 'point_of_sale'],

    # Data files
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],

    # Assets
    'assets': {
        'point_of_sale._assets_pos': [
            'cs_hide_pos_fields/static/src/js/pos_override.js',
        ],
    },

    # Demo data
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
