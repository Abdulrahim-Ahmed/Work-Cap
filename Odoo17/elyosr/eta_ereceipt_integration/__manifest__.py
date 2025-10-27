# -*- coding: utf-8 -*-
{
    'name': "ETA E-Receipt",
    'summary': """
    'version': '17.0.1.0.0',
    """,
    'description': """
    """,
    'author': 'Mario Roshdy',
    'website': "www.linkedin.com/in/mario-roshdy-ba8688169",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/pos_device_config_view.xml',
        'views/pos_config_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/account_tax_view.xml',
        'views/uom_uom_view.xml',
        'views/pos_payment_method_view.xml',
        'views/pos_order_view.xml',
    ],
}