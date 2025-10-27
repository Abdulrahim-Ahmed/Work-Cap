# -*- coding: utf-8 -*-
{
    'name': "Cutting List",
    'summary': """                """,
    'description': """     Cutting list Model for manufacture furniture    """,
    'author': "Cap-Stone Solutions",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '17.0.0.1',
    'license': "AGPL-3",
    'depends': ['base', 'stock', 'sale', 'mrp'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
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
