# -*- coding: utf-8 -*-
{
    'name': 'Pos Access Right',
    'version': '18.0',
    'category': 'Sales/Point Of Sale',
    'summary': 'Pos Access Right',
    'description': """
        Pos Access Right
    """,
    'author': 'Capstone Solution',
    'website': 'https://www.capstone-solution.com',
    'depends': ['web', 'point_of_sale', 'pos_hr'],
    'data': [
        "views/res_config_settings.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "/wt_pos_access_right/static/src/overrides/models/pos_store.js",
            "/wt_pos_access_right/static/src/app/screens/product_screen/product_screen.js",
            "/wt_pos_access_right/static/src/app/screens/ticket_screen/ticket_screen.js",
        ],
    },
    'images': ['static/images/pos_access.jpg'],
    'price': 00.00,
    'currency': "USD",
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
