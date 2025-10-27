# -*- coding: utf-8 -*-
{
    'name': "Extra Rights",

    'summary': "This model is adding a access right group for product Sales Price field, cost, margins "
               "and Cancel Button ",

    'description': """
This model is adding a access right group for product Sales Price field, cost, margins "
               "and Cancel Button
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'sale_margin'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'security/groups.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
