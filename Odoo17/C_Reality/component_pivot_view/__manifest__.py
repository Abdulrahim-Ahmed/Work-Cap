# -*- coding: utf-8 -*-
{
    'name': "Component In Pivot View",

    'summary': """
       This model adding component field names of each product in the pivot view of mrp""",

    'description': """
        This model adding component field names of each product in the pivot view of mrp
    """,

    'author': "Capstone Solution",
    'website': "http://www.capstone-solutions.com",
    'category': 'Uncategorized',
    'version': '17.0.0.1',
    'depends': ['base', 'mrp'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
