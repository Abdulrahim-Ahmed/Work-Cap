
# -*- coding: utf-8 -*-
{
    'name': "Purchase Approval Cycle",

    'summary': """ Purchase 2 Levels Approval Cycle """,

    'description': """
        This model to add 2 steps approval cycle between Purchase quotation and Purchase order and if there is any 
        changes happened the system will ignore to confirm the order unless the order get 2 approvals again after the
        second approval
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
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
