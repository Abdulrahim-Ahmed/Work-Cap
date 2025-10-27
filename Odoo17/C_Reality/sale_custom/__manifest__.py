# -*- coding: utf-8 -*-
{
    'name': "Sale Custom",

    'summary': """ This model adding some fields in product & product variant screen and relate it to sales screen 
                    & add another photo to product and view it print invoice""",

    'description': """ This model adding some fields in product & product variant screen and relate it to sales screen 
                    & add another photo to product and view it print invoice""",
    'author': "Capstone Solutions",
    'website': "http://www.capstonesolution.com",
    'category': 'Uncategorized',
    'version': '17.0.0.1',
    'license': "AGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['product', 'base', 'sale', 'mrp', 'account_intrastat'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
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
