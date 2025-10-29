# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryCatalog(http.Controller):
#     @http.route('/inventory_catalog/inventory_catalog', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_catalog/inventory_catalog/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_catalog.listing', {
#             'root': '/inventory_catalog/inventory_catalog',
#             'objects': http.request.env['inventory_catalog.inventory_catalog'].search([]),
#         })

#     @http.route('/inventory_catalog/inventory_catalog/objects/<model("inventory_catalog.inventory_catalog"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_catalog.object', {
#             'object': obj
#         })

