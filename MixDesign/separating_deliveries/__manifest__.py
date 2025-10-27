# -*- coding: utf-8 -*-
{
    'name': "Delivery Separate",

    'summary': ""
               "This model separating deliverys for each order line to be in single delivery"
               "Adding Char field for GRN in form, list, filter and groupe by "
               "modify the stock.picking model with a boolean field is_multi_line to set to True "
               "if there is more than one stock move (line) inside that picking.",

    'description': """
            "This model separating deliverys for each order line to be in single delivery"
            "Adding Char field for GRN in form, list, filter and groupe by "
            "modify the stock.picking model so that a boolean field is_multi_line is set to True "
            "if there is more than one stock move (line) inside that picking."
            """,
            
    'author': "Capstone Solution",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.0.2',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}