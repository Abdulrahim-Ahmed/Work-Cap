# -*- coding: utf-8 -*-
{
    'name': "invoice_bill_value",

    'summary': "Automatically set the default journal in Odoo 18 based on the invoice type. Use XML to assign Customer Invoices for invoices and Vendor Bills for bills.",

    'description': """
Automatically set the default journal in Odoo 18 based on the invoice type. Use XML to assign Customer Invoices for invoices and Vendor Bills for bills
    """,

    'author': "capstone-solution",
    'website': "https://www.capstone-solution.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

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

