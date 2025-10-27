# -*- coding: utf-8 -*-
{
    'name': "Sales Person",

    'summary': "This model adding a sales person in sales order that related to employee then to add it to the sales pivot view",

    'description': """
This model adding a sales person in sales order that related to employee then to add it to the sales pivot view
    """,

    'author': "Capstone Solution",
    'website': "https://www.capstonesolution.com",
    'category': 'Uncategorized',
    'version': '18.0.1.2',
    'depends': ['base', 'sale', 'documents_hr'],
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
