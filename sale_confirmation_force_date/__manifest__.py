# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Sale Confirmation Date - Sale Back Date",
    "version": "16.0.0.0",
    "category": "Sales",
    'summary': 'Sale confirmation date Sale order confirmation date Sale confirmation force date Sale order '
               'confirmation date sale confirmation backdate sale order confirmation back date sales back date sale '
               'backdate sales backdate sale order backdate sale back date sale',
    "description": """
                     This odoo app helps user to select sale confirmation date,
                      selected date also reflect on delivery order only if delivery date not selected in sale order. 
                """,
    'author': "My Company",
    'website': "http://www.deverst.co",

    "depends": ['base', 'sale', 'stock', 'sale_management'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/sale_confirm_force_date_view.xml',
    ],
    "license": 'OPL-1',
    'qweb': [],
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
