# -*- coding: utf-8 -*-
{
    'name': "Pos Scrap From Pos Session",

    'summary': "This module adds a scrap button inside POS order session that allows scrapping multiple products at once",

    'description': """
This module adds a scrap button inside POS order session that allows users to:
- Scrap single or multiple products at once
- Select quantities for each product individually
- Apply analytic accounts from POS session
- Create stock scrap records with proper inventory tracking
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/templates.xml',
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_custom_popup_button/static/src/js/custom_button.js',
            'pos_custom_popup_button/static/src/js/scrap_popup.js',
            'pos_custom_popup_button/static/src/xml/custom_button.xml',
            'pos_custom_popup_button/static/src/xml/scrap_popup.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
