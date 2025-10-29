# -*- coding: utf-8 -*-
{
    'name': "Operations Drop Down List",

    'summary': """
       This Model to force user to choose from drop down list for operations to prevent duplication of 
       (Operation name) in Manufacturing """,

    'description': """
        This Model to force user to choose from drop down list for operations to prevent duplication of 
       (Operation name) in Manufacturing
    """,

    'author': "CapStone Solutions",
    'website': "https://www.capstone-solution.com",
    'email': "info@capstone-solution.com",
    'category': 'Manufacture',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/operation_name.xml',
        'views/inherit_main_operation.xml',
        'views/inherit_main_operation_tree.xml',
        'views/inherit_main_workcenter.xml',

    ],
    'installable': True,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
