{
    "name": "cs_pos_cancel_order_history",
    "description": """Using this mdoule you can cancel Complete Order and order line Cancel with reason. This module you can use for Restaurant as well as for keep track of the POS cancel order with reaosn and history . With this module you can get the report of cancelled order with reason.""",
    'summary': 'Using this mdoule you can cancel Complete Order and order line Cancel with reason. This module you can use for Restaurant as well as for keep track of the POS cancel order with reaosn and history . With this module you can get the report of cancelled order with reason.',
    "version": "18.0.3.2.1",
    'category': 'Point of Sale',
    'author': 'Capstone Solutions',
    'sequence': 1,
    'email': 'dotsprime@gmail.com',
    'support': 'sales@dotsprime.com',
    "website": 'https://dotsprime.com/',
    "license": 'OPL-1',
    "price": 33,
    "currency": "EUR",
    'depends': ['point_of_sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'security/pos_order_cancel_company_rule.xml',
        'data/pos_cancel_reason_data.xml',
        'views/pos_config_view.xml',
        'views/report_saledetails.xml',
        'views/pos_cancel_reason_view.xml',
        'views/pos_order_cancel_view.xml',
    ],

    # __manifest__.py
    'assets': {
        'web.assets_backend': [
            'cs_pos_cancel_order_history/static/src/js/pos_cancel_list_view.js',
        ],
        'point_of_sale._assets_pos': [
            'cs_pos_cancel_order_history/static/src/js/cancel_reason_popup.js',
            'cs_pos_cancel_order_history/static/src/js/ticket_screen.js',
            'cs_pos_cancel_order_history/static/src/js/order_line_delete_popup.js',
            'cs_pos_cancel_order_history/static/src/xml/cancel_reason_popup.xml',
        ],
    },

    'demo': [],
    "live_test_url": "",
    "images": ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
