# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Blanket Sales Order | Sales Blanket Order',
    'version': '18.0.0.0',
    'category': 'Sales',
    'summary': 'Create blanket sales order manage blanket order sale blanket orders for sales process sales agreement blanket sale order sales blanket orders blanket sale orders from from blanket order quotation blanket order sale order for blanket order',
    'description': """Sales Blanket Order Odoo App is a versatile tool designed to streamline and optimize the sales order management process for businesses. This app allows businesses to create blanket sales orders and add products with different quantities and set expiry dates. Users can create sales quotations with different customers and quantities from blanket sale order.""",
    'author': 'BROWSEINFO',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_sales_blanket_order&version=18&edition=Community',
    "price": 19,
    'license': 'OPL-1',
    "currency": 'EUR',
    'depends': ['base', 'sale_management','stock'],
    'data': [
        'security/blanket_order_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/quotation_wizard_view.xml',
        'views/blanket_order_views.xml',
        'views/sale_order_line.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.browseinfo.com/demo-request?app=bi_sales_blanket_order&version=18&edition=Community',
    "images": ['static/description/Banner.gif'],
}
