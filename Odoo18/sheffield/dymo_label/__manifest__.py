# -*- coding: utf-8 -*-
{
    'name': "Dymo Label Barcode Size",

    'summary': "This model is editing on the barcode number in the dymo print label",

    'description': """
This model is editing on the barcode number in the dymo print label
    """,

    'author': "Capstone-Solutions",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'depends': ['base', 'product', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/label_print.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

