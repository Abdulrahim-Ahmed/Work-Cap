# -*- coding: utf-8 -*-
{
    'name': "Check Management",

    'summary': """
        Checque managment Cycle, Complete Check Management module for Odoo 18 with full functionality for handling cheque transactions""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Capstone Solutions",
    'website': "http://www.capstone-solutions.com",
    'category': 'account',
    'version': '18.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group_user.xml',

        'views/cheque_recieve_view.xml',
        'views/views.xml',
        'views/config.xml',
        'views/payment_actions.xml',
        'views/cheque_send_view.xml',
        'views/cheque_document.xml',
        'reports/payment_voucher.xml',
        'reports/receipt_voucher.xml',
        'reports/invoices.xml',

    ],

}
