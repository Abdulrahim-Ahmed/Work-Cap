
# -*- coding: utf-8 -*-
{
    'name': "Sales Single Approval Cycle",

    'summary': """ Sales Single Approval Cycle """,

    'description': """
        This model to add approval between Sales quotation and Sales order
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '17.0.1.0',
    'depends': ['base', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
