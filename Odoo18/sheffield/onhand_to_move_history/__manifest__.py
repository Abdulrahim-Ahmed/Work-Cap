# -*- coding: utf-8 -*-
{
    'name': "On Hand In Move History",

    'summary': "This model is adding a onhand field in moves history",

    'description': """
This model is adding a onhand field in moves history    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'depends': ['base', 'stock'],
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

