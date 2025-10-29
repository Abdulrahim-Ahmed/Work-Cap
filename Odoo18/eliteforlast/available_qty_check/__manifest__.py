# -*- coding: utf-8 -*-
{
    'name': "All Available Qty",

    'summary': "This module adds a all_available field to both Sales Order Form and Sale Order List.",

    'description': """
This module adds a all_available field to both Sales Orders and Sale Order List.
that compute is all selected lines is available in the mentioned location or not and give availability to group
by with the True and False in the List view
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

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

