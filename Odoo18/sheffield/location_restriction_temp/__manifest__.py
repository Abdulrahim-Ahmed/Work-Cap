# -*- coding: utf-8 -*-
{
    'name': "Location Restriction Users",

    'summary': "This module is adding allowed source location field in user/preferences to choose the "
               "allowed locations for this user",

    'description': """
This module is adding allowed source location field in user/preferences to choose the "
               "allowed locations for this user
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
