# -*- coding: utf-8 -*-
{
    'name': "Margin Access Right & Discount Field",
    'summary': "This model is restricting view of margins in pos orders to be with setting access right group and "
               "editing on Discount field in the same place to be 6 Digits after decimal point instead of 2",

    'description': """
This model is restricting view of margins in pos orders to be with setting access right group and editing on 
Discount field in the same place to be 6 Digits after decimal point instead of 2""",

    'author': "Capstone Solutions",
    'website': "https://www.capstonesolutions.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'depends': ['base', 'point_of_sale', 'sale_management', 'sale_margin'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/sale_order.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
