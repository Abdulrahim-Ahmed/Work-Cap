# -*- coding: utf-8 -*-

{
    'name': "Warehouse Restrictions",

    'summary': """
         Warehouse and Stock Locations, Picking types and picking Restriction on Users.""",
    'description': """
        This Module Restricts the User from Accessing Warehouse and Process Stock Moves other than allowed to Warehouses and Stock Locations.
    """,

    'author': "Frog",
    'website': "https://www.devest.co",

    'category': 'Warehouse',
    'version': '18.0.2.2',

    'depends': ['base', 'stock'],

    'data': [
        'views/users.xml',
        'security/security.xml',
    ],
    "images": [
        'static/description/icon.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
