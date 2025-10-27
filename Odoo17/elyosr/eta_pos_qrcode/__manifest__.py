# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Egypt - Point of Sale QR',
    'author': 'Mario',
    'category': 'Point of Sale',
    'description': """
Egypt POS Localization
=======================================================
    """,
    'license': 'LGPL-3',
    'depends': ['eta_ereceipt_integration'],
    'data': [
        'views/views.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'eta_pos_qrcode/static/src/js/models.js',
            'eta_pos_qrcode/static/src/js/reprint_receipt_button.js',
            # 'eta_pos_qrcode/static/src/xml/order_receipt.xml',
        ],
    },
}
