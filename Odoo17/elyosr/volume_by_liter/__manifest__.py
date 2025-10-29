# -*- coding: utf-8 -*-
{
    'name': "Volume By Liter",

    'summary': "This module adding volume by liter to the product page then to add it to the reports of sales & purchase analysis",

    'description': """
This module adding volume by liter to the product page then to add it to the reports of sales & purchase analysis    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/variants.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

