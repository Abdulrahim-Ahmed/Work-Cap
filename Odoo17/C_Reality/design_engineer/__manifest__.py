# -*- coding: utf-8 -*-
{
    'name': "design_engineer",
    'summary': """      add field to model product                        """,
    'description': """        model to company c-riality    """,
    'author': "Abd El-hamed Saad",
    'website': "http://www.deverst.co",
    'category': 'Uncategorized',
    'version': '0.16',
    'license': "AGPL-3",
    'depends': ['base','product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
