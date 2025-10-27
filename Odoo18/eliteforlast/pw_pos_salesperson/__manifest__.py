# -*- coding: utf-8 -*-
{
    'name': 'POS Salesperson',
    'version': '18.0.0.1',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'hr'],
    'summary': 'This apps helps you set salesperson on pos orderline from pos interface | POS Orderline User | Assign Sales Person on POS | POS Sales Person',
    'description': """
- Odoo POS Orderline user
- Odoo POS Orderline salesperson
- Odoo POS Salesperson
- Odoo POS Item Salesperson
- Odoo POS Item User
- Odoo POS product salesperson
    """,
    'data': [
        'views/res_config_setting_view.xml',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'report/pos_session_sales_details_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pw_pos_salesperson/static/src/js/pos_order_patch.js',
            'pw_pos_salesperson/static/src/js/pos_order_line_patch.js',
            'pw_pos_salesperson/static/src/js/models.js',
            'pw_pos_salesperson/static/src/js/SalespersonVisualManager.js',
            'pw_pos_salesperson/static/src/js/SalespersonButton.js',
            'pw_pos_salesperson/static/src/js/OrderlineSalespersonIcon.js',
            'pw_pos_salesperson/static/src/js/OrderlinePatch.js',
            'pw_pos_salesperson/static/src/js/control_buttons.js',
            'pw_pos_salesperson/static/src/xml/pos.xml',
            # 'pw_pos_salesperson/static/src/xml/receipt.xml',  # Still disabled
        ],
    },
    'price': 20.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    'live_test_url': 'https://youtu.be/xnM8rchcD2o',
    "images":["static/description/Banner.png"],
}
