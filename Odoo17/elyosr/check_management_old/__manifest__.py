# -*- coding: utf-8 -*-
{
    'name': "Checque Management V4",

    'summary': """
        Checque managment Cycle""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Capstone Solutions",
    'website': "http://www.capstone-solutions.com",
    'category': 'account',
    'version': '17.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

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
