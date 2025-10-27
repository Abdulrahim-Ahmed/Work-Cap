# -*- coding: utf-8 -*-
{
    'name': "Invoicing Order Lines",

    'summary': "This model adding new menuitem inside Sales module to be able to see the sale order lines separately "
               "inorder to invoice the selected order lines depending on customer",

    'description': """
This model adding new menuitem inside Sales module to be able to see the sale order lines separately
               inorder to invoice the selected order lines depending on customer
    """,
    'author': "capstone solution",
    'website': "https://www.capstonesolution.com",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'depends': ['base', 'sale', 'bi_sales_blanket_order', 'separating_deliveries'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/invoiced_lines.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

