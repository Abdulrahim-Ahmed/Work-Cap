# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Purchase Confirmation Force Date - Back Date in Odoo",
    "version" : "16.0.0.0",
    "category" : "Purchases",
    'summary': 'Purchase confirmation date purchase order confirmation date purchase force date purchase order confirmation date purchase confirmation backdate purchase confirm back date purchase backdate purchase order backdate purchase back date PO backdate on purchase',
    "description": """
                  This odoo app helps user to select purchase confirmation date, selected date also reflect on purchase order receipt only if receipt date ont selected in purchase order.
                """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 15,
    "currency": 'EUR',
    "depends" : ['base','purchase','stock'],
    "data": ['security/ir.model.access.csv',
            'wizard/purchase_confirm_force_date_view.xml',
            ],
    'qweb': [],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/bOOPk9iNdLE',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
