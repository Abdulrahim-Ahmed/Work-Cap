# -*- coding: utf-8 -*-
{
    'name': "Monetary Custody",

    'summary': """
        Monetary Custody""",

    'description': """
        Monetary Custody
    """,

    'author': "SMAC",
    'website': "https://www.yourcompany.com",
    'version': '18.0.0.1',
    'depends': ['base', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/request_cash_custody.xml',
        'views/reconcile_custody.xml',
        'views/account_move.xml',
        'data/data.xml',
    ],
}
