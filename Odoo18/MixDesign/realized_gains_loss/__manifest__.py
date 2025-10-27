# -*- coding: utf-8 -*-
{
    'name': "realized_gains_loss",

    'summary': "This Model is to create a realized Gains/Losses report but needs to be setting up from UI system that "
               "adds the report manually & Editing on the assets tree view",

    'description': """
Long description of module's purpose
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'accountant', 'account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

