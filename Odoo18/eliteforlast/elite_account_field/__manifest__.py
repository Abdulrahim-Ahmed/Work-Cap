# -*- coding: utf-8 -*-
{
    'name': "Account & Analytic Account Access Right",

    'summary': "Adding access right group to Account & Analytic Account fields in invoice/bill and journals",

    'description': """
Adding access right group to Account & Analytic Account fields in invoice/bill and journals
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'security/account_access_group.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
